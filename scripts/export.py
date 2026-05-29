import os
import sqlite3
from pathlib import Path

# Paths resolvidos relativamente à localização deste script (scripts/)
BASE_DIR     = Path(__file__).parent.parent           # raiz do projeto
mbtiles_path = BASE_DIR / "data" / "mbtiles" / "insa_layers.mbtiles"
output_dir   = BASE_DIR / "public" / "tiles" / "insa_layers"

os.makedirs(output_dir, exist_ok=True)

print(f"📦 Abrindo banco de dados: {mbtiles_path}")
conn = sqlite3.connect(mbtiles_path)
cursor = conn.cursor()

cursor.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles;")

count = 0
for row in cursor:
    zoom, col, t_row, data = row

    # Inversão Flip Y: MBTiles usa TMS, a web usa XYZ
    y = (1 << zoom) - 1 - t_row

    tile_dir = output_dir / str(zoom) / str(col)
    os.makedirs(tile_dir, exist_ok=True)

    tile_path = tile_dir / f"{y}.pbf"
    with open(tile_path, "wb") as f:
        f.write(data)

    count += 1
    if count % 1000 == 0:
        print(f" ➜ {count} blocos (.pbf) extraídos...")

conn.close()
print(f"✨ Sucesso total! {count} blocos extraídos em '{output_dir}/'")
