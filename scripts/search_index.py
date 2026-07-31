"""
Gera src/assets/search_index.json — os valores de atributo (sem geometria)
de toda camada espacial do GeoPackage, usados pela busca do frontend
(`matchesFilter` em mapRenderer.js) no lugar de escanear tiles MVT já
carregados na tela.

Por quê: a busca antiga contava resultados só nos tiles que o navegador já
tinha buscado pra renderizar (cache de tiles da viewport atual) — uma feição
que bate com o filtro mas está fora da área/zoom visível no momento da busca
nunca era vista, mostrando "Nenhum resultado encontrado" mesmo a feição
existindo. Vetor tiles em zoom baixo também descartam/simplificam feições
pequenas por natureza (ver "Manutenção do GeoPackage" e o comando do
Tippecanoe no CLAUDE.md), então nem um fetch dedicado de zoom baixo garante
cobertura completa pra camadas densas (ex. ivd_sab, ~9.7 mil polígonos). Um
índice à parte, direto do GeoPackage, é a única forma de garantir que a
busca sempre veja o dado inteiro, não importa o que está na tela.

Rodar da raiz do projeto: python scripts/search_index.py
"""

import json
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
GPKG = BASE_DIR / "data" / "dados_insa.gpkg"
OUTPUT_JSON = BASE_DIR / "src" / "assets" / "search_index.json"

# Tabelas não espaciais do QGIS — não são camadas da aplicação.
EXCLUDE = {"qgis_projects", "layer_styles"}


def main():
    con = sqlite3.connect(GPKG)
    cur = con.cursor()

    cur.execute("SELECT table_name, column_name FROM gpkg_geometry_columns")
    geom_cols = dict(cur.fetchall())

    cur.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features' ORDER BY table_name")
    tables = [r[0] for r in cur.fetchall() if r[0] not in EXCLUDE]

    result = {}
    for table in tables:
        geom_col = geom_cols.get(table)
        cur.execute(f'PRAGMA table_info("{table}")')
        fields = [c[1] for c in cur.fetchall() if c[1] not in ("fid", geom_col)]
        if not fields:
            # ex. focos_queimadas — só geometria, nada pra buscar
            result[table] = []
            print(f"—  {table} (sem campos)")
            continue
        cols_sql = ", ".join(f'"{f}"' for f in fields)
        cur.execute(f'SELECT {cols_sql} FROM "{table}"')
        rows = [dict(zip(fields, row)) for row in cur.fetchall()]
        result[table] = rows
        print(f"✓  {table} (campos: {fields}, {len(rows)} feições)")

    con.close()

    os.makedirs(OUTPUT_JSON.parent, exist_ok=True)
    # Compacto (sem indent) — arquivo gerado/consumido só por código, nunca
    # editado à mão, e algumas camadas têm milhares de linhas (ex. ivd_sab).
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(OUTPUT_JSON) // 1024
    total_rows = sum(len(v) for v in result.values())
    print(f"\nConcluído: {len(result)} camadas, {total_rows} feições indexadas")
    print(f"Arquivo gerado: {OUTPUT_JSON} ({size_kb} KB)")


if __name__ == "__main__":
    main()
