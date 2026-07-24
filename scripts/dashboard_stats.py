import json
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

from geo_utils import TARGET_CRS, classify_categorized, classify_graduated, fix_geometries

BASE_DIR    = Path(__file__).parent.parent
GPKG        = BASE_DIR / "data" / "dados_insa.gpkg"
STYLES_JSON = BASE_DIR / "src" / "assets" / "styles.json"
OUTPUT_JSON = BASE_DIR / "src" / "assets" / "dashboard_stats.json"

MUNICIPIOS_LAYER = "municipios_pb_semiarido"

# Camadas de índice compostas elegíveis para o cruzamento com municípios.
INDEX_LAYERS = ["ivs", "ivv", "ivc", "ivm", "ivd_sab"]

COVERAGE_WARN_THRESHOLD = 0.95


def load_municipios():
    gdf = gpd.read_file(GPKG, layer=MUNICIPIOS_LAYER).to_crs(TARGET_CRS)
    gdf = gdf[["cod_ibge_m", "nm_municip", "slug", "geometry"]]
    return fix_geometries(gdf)


def classify_series(gdf, field, style):
    classes_meta = style["classes"]
    if style["type"] == "categorized":
        return gdf[field].apply(lambda v: classify_categorized(v, classes_meta))
    sorted_classes = sorted(classes_meta, key=lambda c: c["max"])
    return gdf[field].apply(lambda v: classify_graduated(v, sorted_classes))


def compute_index(municipios, layer_name, style):
    field = style["field"]
    gdf = gpd.read_file(GPKG, layer=layer_name).to_crs(TARGET_CRS)
    gdf = fix_geometries(gdf)
    gdf["_class"] = classify_series(gdf, field, style)
    gdf = gdf[["_class", field, "geometry"]].dropna(subset=[field])

    overlay = gpd.overlay(municipios, gdf, how="intersection", keep_geom_type=True)
    overlay["_area"] = overlay.geometry.area  # m² — só usado como peso

    # ── Validação de cobertura: fatias somadas vs área do município ────────────
    frag_by_muni = overlay.groupby("cod_ibge_m")["_area"].sum()
    muni_area = municipios.set_index("cod_ibge_m").geometry.area
    coverage_ratio = (frag_by_muni / muni_area).reindex(muni_area.index)
    low_coverage = coverage_ratio[coverage_ratio < COVERAGE_WARN_THRESHOLD]
    if len(low_coverage):
        print(
            f"  ⚠️  {layer_name}: {len(low_coverage)} municípios com cobertura < "
            f"{int(COVERAGE_WARN_THRESHOLD * 100)}% (ex.: {low_coverage.index[:5].tolist()})"
        )

    # ── Valor médio ponderado por área ──────────────────────────────────────────
    overlay["_weighted"] = overlay[field] * overlay["_area"]
    weighted = (
        overlay.groupby("cod_ibge_m")
        .apply(lambda g: g["_weighted"].sum() / g["_area"].sum(), include_groups=False)
    )

    # ── Classe dominante (maior área agregada) ──────────────────────────────────
    class_area = (
        overlay.dropna(subset=["_class"])
        .groupby(["cod_ibge_m", "_class"])["_area"].sum()
        .reset_index()
    )
    dominant = pd.Series(dtype=object)
    if len(class_area):
        dominant = (
            class_area.loc[class_area.groupby("cod_ibge_m")["_area"].idxmax()]
            .set_index("cod_ibge_m")["_class"]
        )

    color_by_label = {c["label"]: c["color"] for c in style["classes"]}

    result = {}
    for cod in municipios["cod_ibge_m"]:
        val = weighted.get(cod)
        cls = dominant.get(cod)
        result[cod] = {
            "value": round(float(val), 3) if pd.notna(val) else None,
            "class_label": cls if pd.notna(cls) else None,
            "class_color": color_by_label.get(cls) if pd.notna(cls) else None,
        }
    return result, field


def main():
    with open(STYLES_JSON, encoding="utf-8") as f:
        styles = json.load(f)

    municipios = load_municipios()
    print(f"📍 {len(municipios)} municípios carregados")

    indices_meta = {}
    per_index = {}
    for layer_name in INDEX_LAYERS:
        style = styles[layer_name]
        print(f"⏳ Processando {layer_name} (campo: {style['field']})...")
        result, field = compute_index(municipios, layer_name, style)
        per_index[layer_name] = result
        indices_meta[layer_name] = {"sourceLayer": layer_name, "field_used": field}
        n_null = sum(1 for v in result.values() if v["value"] is None)
        print(f"✓  {layer_name} — {n_null} municípios sem cobertura")

    municipios_out = {}
    for _, row in municipios.iterrows():
        cod = row["cod_ibge_m"]
        municipios_out[cod] = {
            "cod_ibge_m": cod,
            "nm_municip": row["nm_municip"],
            "slug": row["slug"],
            "indices": {key: per_index[key][cod] for key in INDEX_LAYERS},
        }

    output = {"indices_meta": indices_meta, "municipios": municipios_out}
    os.makedirs(OUTPUT_JSON.parent, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(OUTPUT_JSON) // 1024
    print(f"\n🚀 Concluído: {len(municipios_out)} municípios × {len(INDEX_LAYERS)} índices")
    print(f"Arquivo gerado: {OUTPUT_JSON} ({size_kb} KB)")


if __name__ == "__main__":
    main()
