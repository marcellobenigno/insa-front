import sqlite3
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

# Paths resolvidos relativamente à localização deste script (scripts/)
BASE_DIR    = Path(__file__).parent.parent           # raiz do projeto
gpkg_file   = BASE_DIR / "data" / "dados_insa.gpkg"
output_json = BASE_DIR / "src" / "assets" / "styles.json"

print(f"🔍 Verificando o arquivo: {gpkg_file}")

if not gpkg_file.exists():
    print(f"❌ Erro: O arquivo {gpkg_file} não foi encontrado.")
    exit(1)

conn = sqlite3.connect(gpkg_file)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='layer_styles';")
if not cursor.fetchone():
    print("❌ Erro: A tabela 'layer_styles' não existe neste GeoPackage. Salve os estilos no QGIS primeiro.")
    conn.close()
    exit(1)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
real_tables = {row[0] for row in cursor.fetchall()}

cursor.execute("SELECT f_table_name, styleQML FROM layer_styles")
rows = cursor.fetchall()

print(f"📋 Total de estilos encontrados no banco: {len(rows)}")


def rgba_to_hex(prop_value):
    """QGIS symbol color prop: '213,187,135,255,rgb:...' -> '#d5bb87'"""
    parts = prop_value.split(",")
    r, g, b = (int(parts[i]) for i in range(3))
    return f"#{r:02x}{g:02x}{b:02x}"


def symbol_colors(renderer_el):
    """Maps symbol name -> hex color for a <renderer-v2>.

    QGIS has used two on-disk formats for symbol layer properties across
    versions: legacy `<prop k="color" v="...">` and the current
    `<Option name="color" type="QString" value="...">`. Support both.
    """
    colors = {}
    symbols_el = renderer_el.find("symbols")
    if symbols_el is None:
        return colors
    for symbol_el in symbols_el.findall("symbol"):
        name = symbol_el.get("name")
        color_value = None
        for prop in symbol_el.findall(".//prop"):
            if prop.get("k") == "color":
                color_value = prop.get("v")
                break
        if color_value is None:
            for opt in symbol_el.findall(".//Option[@name='color']"):
                color_value = opt.get("value")
                break
        if color_value:
            colors[name] = rgba_to_hex(color_value)
    return colors


def extract_layer_style(qml_text):
    """Returns {type, field, classes: [...]} or None if unsupported/unparseable."""
    try:
        root = ET.fromstring(qml_text)
    except ET.ParseError:
        return None

    renderer_el = root.find(".//renderer-v2")
    if renderer_el is None:
        return None

    renderer_type = renderer_el.get("type")
    colors = symbol_colors(renderer_el)

    if renderer_type == "graduatedSymbol":
        ranges_el = renderer_el.find("ranges")
        if ranges_el is None:
            return None
        classes = []
        for r in ranges_el.findall("range"):
            classes.append({
                "max": float(r.get("upper")),
                "label": clean_label(r.get("label")),
                "color": colors.get(r.get("symbol"), "#9ca3af"),
            })
        classes.sort(key=lambda c: c["max"])
        return {"type": "graduated", "field": renderer_el.get("attr"), "classes": classes}

    if renderer_type == "categorizedSymbol":
        categories_el = renderer_el.find("categories")
        if categories_el is None:
            return None
        classes = []
        for cat in categories_el.findall("category"):
            value = cat.get("value")
            try:
                value = float(value)
            except (TypeError, ValueError):
                # Classificação por texto (ex. solos_textura, tipos_solo,
                # geologia) — mantém a string como veio do QML em vez de
                # descartar a categoria. mapRenderer.js/geo_utils.py fazem
                # correspondência exata case-insensitive nesse caso.
                pass
            classes.append({
                "value": value,
                "label": clean_label(cat.get("label")),
                "color": colors.get(cat.get("symbol"), "#9ca3af"),
            })
        classes.sort(key=lambda c: c["value"] if isinstance(c["value"], float) else str(c["value"]))
        return {"type": "categorized", "field": renderer_el.get("attr"), "classes": classes}

    if renderer_type == "singleSymbol":
        symbols_el = renderer_el.find("symbols")
        first_symbol = symbols_el.find("symbol") if symbols_el is not None else None
        name = first_symbol.get("name") if first_symbol is not None else None
        return {"type": "single", "field": None, "classes": [
            {"label": "Padrão", "color": colors.get(name, "#9ca3af")}
        ]}

    return None


def clean_label(label):
    """Strips whitespace and normalizes QGIS-authored labels (e.g. '1,4 - Alta ' -> '1,4 - Alta')."""
    return (label or "").strip()


def real_field_name(table_name, qml_field):
    """Resolve o `attr` do QML pro nome de coluna real da tabela.

    SQLite (e portanto o GeoPackage) faz lookup de coluna case-insensitive,
    mas o export pra GeoJSON/MVT preserva a caixa real da coluna — um QML
    que referencia `DSC_TEXTUR` quando a coluna de verdade é `dsc_textur`
    nunca dá erro no QGIS (silenciosamente tolerante), mas `style.field`
    nunca bateria com `feature.properties` no frontend, pintando a camada
    inteira de cinza (ver solos_textura/geologia no CLAUDE.md)."""
    if qml_field is None:
        return qml_field
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    for col in cursor.fetchall():
        if col[1].lower() == qml_field.lower():
            return col[1]
    return qml_field


# Linhas de layer_styles cujo f_table_name é de uma entrega anterior do
# GeoPackage (a tabela foi renomeada, mas a linha de estilo ficou órfã com o
# nome antigo) — mapeadas pro nome de tabela real atual. Só preenchem uma
# camada que não tenha sua própria linha de estilo (uma tabela real nunca é
# sobrescrita por uma linha órfã).
RENAMED_TABLES = {
    "geologia_tipos_litologicos": "geologia",
}

styles_map = {}


def process_row(table_name, qml, target_table):
    style = extract_layer_style(qml)
    if style is None or not style["classes"] or style["type"] == "single":
        # singleSymbol layers (e.g. municipios_pb_semiarido) are handled as
        # manual stroke-only entries — see CLAUDE.md.
        return
    style["field"] = real_field_name(target_table, style["field"])
    styles_map[target_table] = style
    labels = [c["label"] for c in style["classes"]]
    suffix = f" (renomeada de {table_name})" if table_name != target_table else ""
    print(f"🎨 {target_table}{suffix} ({style['type']}, campo={style['field']}) -> {labels}")


for table_name, qml in rows:
    if qml and table_name in real_tables:
        process_row(table_name, qml, table_name)

for table_name, qml in rows:
    target_table = RENAMED_TABLES.get(table_name)
    if qml and target_table and target_table in real_tables and target_table not in styles_map:
        process_row(table_name, qml, target_table)

conn.close()

if styles_map:
    os.makedirs(output_json.parent, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(styles_map, f, indent=2, ensure_ascii=False)
    print(f"\n🚀 SUCESSO! Estilos gerados em: {output_json}")
else:
    print("\n❌ Erro: Não foi possível extrair nenhum estilo temático válido do QML.")
