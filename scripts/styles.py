import sqlite3
import re
import json
import os
from pathlib import Path

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

cursor.execute("SELECT f_table_name, styleSLD FROM layer_styles")
rows = cursor.fetchall()

print(f"📋 Total de estilos encontrados no banco: {len(rows)}")

styles_map = {}

for table_name, sld_text in rows:
    if not sld_text:
        continue

    layer_colors = {}

    rules = re.findall(r'<se:Rule>.*?</se:Rule>', sld_text, re.DOTALL)

    for rule in rules:
        fill_match = re.search(r'name="fill"\s*>\s*(#[A-Fa-f0-9]{6}|#[A-Fa-f0-9]{3})', rule)

        if fill_match:
            color = fill_match.group(1)
            literal_match = re.search(r'<ogc:Literal>(.*?)</ogc:Literal>', rule)

            if literal_match:
                value = literal_match.group(1).strip()
                if value and not any(op in value for op in ['<=', '>=', '<', '>', '==']):
                    layer_colors[value] = color
                else:
                    numeric_fallback = re.findall(r'-?\d+\.?\d*', value)
                    if numeric_fallback:
                        layer_colors[numeric_fallback[-1]] = color
                    elif "default" not in layer_colors:
                        layer_colors["default"] = color
            else:
                deep_literal_match = re.findall(r'<ogc:Literal\s*[^>]*>(.*?)</ogc:Literal>', rule, re.DOTALL)
                if deep_literal_match:
                    value = deep_literal_match[-1].strip()
                    layer_colors[value] = color
                else:
                    if "default" not in layer_colors:
                        layer_colors["default"] = color

    if not layer_colors:
        any_fill = re.search(r'name="fill"\s*>\s*(#[A-Fa-f0-9]{6}|#[A-Fa-f0-9]{3})', sld_text)
        if any_fill:
            layer_colors["default"] = any_fill.group(1)

    if layer_colors:
        styles_map[table_name] = layer_colors
        print(f"🎨 Estilo mapeado para: {table_name} -> {list(layer_colors.keys())}")

conn.close()

if styles_map:
    os.makedirs(output_json.parent, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(styles_map, f, indent=2, ensure_ascii=False)
    print(f"\n🚀 SUCESSO! Estilos gerados em: {output_json}")
else:
    print("\n❌ Erro: Não foi possível extrair nenhum estilo temático válido do SLD.")
