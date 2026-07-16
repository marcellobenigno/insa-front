import json
import os
from pathlib import Path

import geopandas as gpd

from geo_utils import TARGET_CRS, classify_categorized, classify_graduated

BASE_DIR    = Path(__file__).parent.parent
GPKG        = BASE_DIR / "data" / "dados_insa.gpkg"
STYLES_JSON = BASE_DIR / "src" / "assets" / "styles.json"
OUTPUT_JSON = BASE_DIR / "src" / "assets" / "stats.json"


def compute_stats(layer_name, style):
    field = style["field"]
    classes_meta = style["classes"]

    gdf = gpd.read_file(GPKG, layer=layer_name)
    if field not in gdf.columns:
        return None, f"campo '{field}' não encontrado na camada"
    gdf = gdf.to_crs(TARGET_CRS)

    if style["type"] == "categorized":
        gdf = gdf.assign(_class=gdf[field].apply(lambda v: classify_categorized(v, classes_meta)))
    else:  # graduated
        sorted_classes = sorted(classes_meta, key=lambda c: c["max"])
        gdf = gdf.assign(_class=gdf[field].apply(lambda v: classify_graduated(v, sorted_classes)))

    gdf_d = gdf.dropna(subset=["_class"]).dissolve(by="_class", as_index=False)
    gdf_d["_area_km2"] = gdf_d.geometry.area / 1e6

    area_by_label = {row["_class"]: round(float(row["_area_km2"]), 1) for _, row in gdf_d.iterrows()}

    # Preserva a ordem autoral do styles.json (QGIS), não a área — garante também
    # que toda classe do estilo apareça no gráfico, mesmo sem polígonos (área 0)
    classes = [
        {"label": c["label"], "area_km2": area_by_label.get(c["label"], 0.0), "color": c["color"]}
        for c in classes_meta
    ]
    total_km2 = round(sum(c["area_km2"] for c in classes), 1)
    return {"classes": classes, "total_km2": total_km2, "field_used": field}, None


def main():
    with open(STYLES_JSON, encoding="utf-8") as f:
        styles = json.load(f)

    result = {}
    processed = 0
    skipped = []

    for layer_name, style in styles.items():
        if style["type"] == "stroke":
            result[layer_name] = None
            skipped.append(f"{layer_name} — stroke-only")
            continue

        data, err = compute_stats(layer_name, style)
        if err:
            result[layer_name] = None
            skipped.append(f"{layer_name} — {err}")
            print(f"⚠️  Pulando {layer_name}: {err}")
        else:
            result[layer_name] = data
            processed += 1
            n = len(data["classes"])
            print(f"✓  {layer_name} (campo: {data['field_used']}, {n} classes)")

    for s in skipped:
        print(f"   Pulando {s}")

    os.makedirs(OUTPUT_JSON.parent, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(OUTPUT_JSON) // 1024
    print(f"\nConcluído: {processed} camadas processadas, {len(skipped)} puladas")
    print(f"Arquivo gerado: {OUTPUT_JSON} ({size_kb} KB)")


if __name__ == "__main__":
    main()
