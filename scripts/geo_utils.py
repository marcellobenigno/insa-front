import pandas as pd

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


def fix_geometries(gdf):
    """Repara geometrias inválidas (self-intersections comuns em polígonos
    derivados de raster) antes de operações sensíveis como overlay."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf.geometry.make_valid()
    return gdf
