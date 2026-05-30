import json
import os
import re
from pathlib import Path

import fiona
import geopandas as gpd
import pandas as pd

BASE_DIR    = Path(__file__).parent.parent
GPKG        = BASE_DIR / "data" / "dados_insa.gpkg"
STYLES_JSON = BASE_DIR / "src" / "assets" / "styles.json"
OUTPUT_JSON = BASE_DIR / "src" / "assets" / "stats.json"

TARGET_CRS       = "EPSG:5880"
MATCH_THRESHOLD  = 0.80
FLOAT_TOL        = 1e-6


def is_stroke_only(layer_styles):
    return all(v.startswith("stroke:") for v in layer_styles.values())


def _parse_floats(keys):
    result = {}
    for k in keys:
        try:
            result[k] = float(k)
        except (ValueError, TypeError):
            pass
    return result


def find_exact_field(gdf, expected_keys):
    n = len(expected_keys)
    if n == 0:
        return None, 0.0, 0

    expected_floats = _parse_floats(expected_keys)
    all_numeric = len(expected_floats) == n
    best_col, best_score, best_n_unique = None, 0.0, 0

    for col in gdf.columns:
        if col == "geometry":
            continue

        unique_vals = gdf[col].dropna().unique()
        n_unique = len(unique_vals)

        unique_str = {str(v) for v in unique_vals}
        score = len(expected_keys & unique_str) / n
        if score > best_score:
            best_col, best_score, best_n_unique = col, score, n_unique
        if best_score >= 1.0:
            break

        if all_numeric and score < MATCH_THRESHOLD:
            try:
                unique_floats = {float(v) for v in unique_vals}
                matched = sum(
                    1 for ef in expected_floats.values()
                    if any(abs(ef - uf) < FLOAT_TOL for uf in unique_floats)
                )
                score_f = matched / n
                if score_f > best_score:
                    best_col, best_score, best_n_unique = col, score_f, n_unique
            except (ValueError, TypeError):
                pass

    if best_score >= MATCH_THRESHOLD:
        return best_col, best_score, best_n_unique
    return None, best_score, 0


def find_ranged_field(gdf, sorted_boundaries):
    lo, hi = sorted_boundaries[0], sorted_boundaries[-1]
    for col in gdf.columns:
        if col == "geometry":
            continue
        series = gdf[col].dropna()
        if not pd.api.types.is_numeric_dtype(series) or len(series) == 0:
            continue
        col_min, col_max = float(series.min()), float(series.max())
        if col_min <= hi and col_max >= lo:
            return col
    return None


def assign_range_class(value, sorted_boundaries):
    try:
        v = float(value)
    except (ValueError, TypeError):
        return None
    for b in sorted_boundaries:
        if v <= b + FLOAT_TOL:
            return b
    return sorted_boundaries[-1]


def parse_label_bounds(keys):
    result = {}
    for k in keys:
        nums = re.findall(r'-?\d+\.?\d*', k)
        if not nums:
            return None
        result[k] = float('inf') if '>' in k else float(nums[-1])
    return result if len(result) == len(keys) else None


def _fill_missing(classes, layer_styles):
    """Append 0-area entries for style keys absent from computed classes."""
    found = {c["label"] for c in classes}
    for key, color in layer_styles.items():
        if key not in found and not color.startswith("stroke:"):
            classes.append({"label": key, "area_km2": 0.0, "color": color})


def compute_stats(layer_name, layer_styles):
    expected_keys = set(layer_styles.keys())
    expected_floats = _parse_floats(expected_keys)
    all_numeric = len(expected_floats) == len(expected_keys)

    gdf = gpd.read_file(GPKG, layer=layer_name)
    gdf = gdf.to_crs(TARGET_CRS)

    field, field_score, n_unique = find_exact_field(gdf, expected_keys)
    # score < 1.0: partial match may be coincidental in a continuous field; redirect to range path
    if field is not None and all_numeric and field_score < 1.0 and n_unique > len(expected_keys) * 2:
        field = None

    if field is not None:
        if pd.api.types.is_numeric_dtype(gdf[field]):
            def normalizar_chave(val):
                try:
                    vf = float(val)
                    for k, kf in expected_floats.items():
                        if abs(vf - kf) < FLOAT_TOL:
                            return k
                except (ValueError, TypeError):
                    pass
                return str(val)
            col = gdf[field].apply(normalizar_chave)
        else:
            col = gdf[field].fillna("Não Informado").astype(str).str.strip()

        gdf_d = gdf.assign(_class=col).dissolve(by="_class", as_index=False)
        gdf_d["_area_km2"] = gdf_d.geometry.area / 1e6

        classes = []
        for _, row in gdf_d.iterrows():
            key = row["_class"]
            color = layer_styles.get(key)
            if color is None:
                continue
            classes.append({"label": key, "area_km2": round(float(row["_area_km2"]), 1), "color": color})

        _fill_missing(classes, layer_styles)
        classes.sort(key=lambda x: x["area_km2"], reverse=True)
        total_km2 = round(sum(c["area_km2"] for c in classes), 1)
        return {"classes": classes, "total_km2": total_km2, "field_used": field}, None

    if all_numeric:
        bounds_map = {v: k for k, v in expected_floats.items()}
        sorted_bounds = sorted(expected_floats.values())
    else:
        label_bounds = parse_label_bounds(expected_keys)
        if label_bounds is None:
            return None, "exact match falhou e chaves não têm intervalos reconhecíveis"
        bounds_map = {v: k for k, v in label_bounds.items()}
        sorted_bounds = sorted(lb for lb in label_bounds.values() if lb != float('inf'))
        if label_bounds and max(label_bounds.values()) == float('inf'):
            sorted_bounds.append(float('inf'))

    finite_bounds = [b for b in sorted_bounds if b != float('inf')]
    field = find_ranged_field(gdf, finite_bounds if finite_bounds else sorted_bounds)
    if field is None:
        return None, "nenhum campo numérico com intervalo compatível encontrado"

    gdf = gdf.assign(
        _class=gdf[field].apply(
            lambda v: bounds_map[assign_range_class(v, sorted_bounds)] if pd.notna(v) else None
        )
    )
    gdf_d = gdf.dropna(subset=["_class"]).dissolve(by="_class", as_index=False)
    gdf_d["_area_km2"] = gdf_d.geometry.area / 1e6

    classes = []
    for _, row in gdf_d.iterrows():
        key = row["_class"]
        color = layer_styles[key]
        classes.append({"label": key, "area_km2": round(float(row["_area_km2"]), 1), "color": color})

    _fill_missing(classes, layer_styles)
    classes.sort(key=lambda x: x["area_km2"], reverse=True)
    total_km2 = round(sum(c["area_km2"] for c in classes), 1)
    return {"classes": classes, "total_km2": total_km2, "field_used": field}, None


def main():
    with open(STYLES_JSON, encoding="utf-8") as f:
        styles = json.load(f)

    available_layers = set(fiona.listlayers(str(GPKG)))

    result = {}
    processed = 0
    skipped = []

    for layer_name, layer_styles in styles.items():
        if is_stroke_only(layer_styles):
            result[layer_name] = None
            skipped.append(f"{layer_name} — stroke-only")
            continue

        if layer_name not in available_layers:
            result[layer_name] = None
            skipped.append(f"{layer_name} — não encontrado no GeoPackage")
            continue

        data, err = compute_stats(layer_name, layer_styles)
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
