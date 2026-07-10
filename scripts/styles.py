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
                continue
            classes.append({
                "value": value,
                "label": clean_label(cat.get("label")),
                "color": colors.get(cat.get("symbol"), "#9ca3af"),
            })
        classes.sort(key=lambda c: c["value"])
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


styles_map = {}

for table_name, qml in rows:
    if not qml or table_name not in real_tables:
        continue

    style = extract_layer_style(qml)
    if style is None or not style["classes"] or style["type"] == "single":
        # singleSymbol layers (e.g. municipios_pb_semiarido) are handled as
        # manual stroke-only entries — see CLAUDE.md.
        continue

    styles_map[table_name] = style
    labels = [c["label"] for c in style["classes"]]
    print(f"🎨 {table_name} ({style['type']}, campo={style['field']}) -> {labels}")

conn.close()

if styles_map:
    os.makedirs(output_json.parent, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(styles_map, f, indent=2, ensure_ascii=False)
    print(f"\n🚀 SUCESSO! Estilos gerados em: {output_json}")
else:
    print("\n❌ Erro: Não foi possível extrair nenhum estilo temático válido do QML.")
