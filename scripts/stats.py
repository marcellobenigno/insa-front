import json
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

BASE_DIR    = Path(__file__).parent.parent
GPKG        = BASE_DIR / "data" / "dados_insa.gpkg"
STYLES_JSON = BASE_DIR / "src" / "assets" / "styles.json"
OUTPUT_JSON = BASE_DIR / "src" / "assets" / "stats.json"

TARGET_CRS = "EPSG:5880"
TOL        = 1e-6


def classify_categorized(value, classes):
    if pd.isna(value):
        return None
    v = float(value)
    best = min(classes, key=lambda c: abs(c["value"] - v))
    return best["label"] if abs(best["value"] - v) < TOL else None


def classify_graduated(value, sorted_classes):
    if pd.isna(value):
        return None
    v = float(value)
    for c in sorted_classes:
        if v <= c["max"] + TOL:
            return c["label"]
    return sorted_classes[-1]["label"]


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

    color_by_label = {c["label"]: c["color"] for c in classes_meta}
    classes = []
    for _, row in gdf_d.iterrows():
        label = row["_class"]
        classes.append({
            "label": label,
            "area_km2": round(float(row["_area_km2"]), 1),
            "color": color_by_label[label],
        })

    # Garante que toda classe do estilo apareça no gráfico, mesmo sem polígonos (área 0)
    found = {c["label"] for c in classes}
    for c in classes_meta:
        if c["label"] not in found:
            classes.append({"label": c["label"], "area_km2": 0.0, "color": c["color"]})

    classes.sort(key=lambda x: x["area_km2"], reverse=True)
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
