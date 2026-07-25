"""
Gera a marca DesertPB (src/assets/logo-mark-fine.svg, logo-mark-coarse.svg,
public/favicon.svg e public/favicon.ico) a partir do contorno real de
limite_semiarido_pb.

Cada "pixel" da marca é um pequeno retângulo, colorido de acordo com o valor
médio real do IVD (camada ivd_sab) naquele ponto do território, classificado
nas mesmas 4 cores/faixas de src/assets/styles.json (ivd_sab) — a marca é uma
miniatura fiel do heatmap real de vulnerabilidade, não uma distribuição
aleatória. Um contorno sutil acompanha o limite real do polígono.

Rodar da raiz do projeto: python scripts/generate_logo.py
Não editar os .svg gerados manualmente — regenerar este script sempre que
limite_semiarido_pb ou ivd_sab mudarem no GeoPackage.
"""

import io
import json
import math
from pathlib import Path

import cairosvg
import geopandas as gpd
import numpy as np
from PIL import Image
from shapely.geometry import box
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = Path(__file__).parent.parent
GPKG = ROOT / "data" / "dados_insa.gpkg"
STYLES_PATH = ROOT / "src" / "assets" / "styles.json"

FINE_OUT = ROOT / "src" / "assets" / "logo-mark-fine.svg"
COARSE_OUT = ROOT / "src" / "assets" / "logo-mark-coarse.svg"
FAVICON_OUT = ROOT / "public" / "favicon.svg"
FAVICON_ICO_OUT = ROOT / "public" / "favicon.ico"
FAVICON_ICO_SIZES = [16, 32, 48, 64, 128, 256]

FINE_COLS = 40
COARSE_COLS = 15
GAP_FRAC = 0.14  # fração da célula usada como espaçamento entre pixels
MIN_COVERAGE = 0.25  # fração mínima da célula (após o gap) dentro do polígono
BORDER_COLOR = "#1a1a1a"
BORDER_OPACITY = 0.55
BORDER_WIDTH = 1.6


def load_classes():
    styles = json.loads(STYLES_PATH.read_text())["ivd_sab"]
    return styles["classes"]


def classify(value, classes):
    for c in classes:
        if value <= c["max"]:
            return c["color"]
    return classes[-1]["color"]


def load_data():
    semiarido = gpd.read_file(GPKG, layer="limite_semiarido_pb")
    poly = unary_union(semiarido.geometry.values)
    ivd = gpd.read_file(GPKG, layer="ivd_sab")[["ivd", "geometry"]]
    return poly, ivd


def build_sampler(ivd_gdf):
    geoms = ivd_gdf.geometry.values
    values = ivd_gdf["ivd"].values
    tree = STRtree(geoms)

    def sample(pt):
        idx = tree.query(pt, predicate="intersects")
        if len(idx) == 0:
            nearest_idx = tree.nearest(pt)
            return values[nearest_idx]
        return float(np.mean(values[idx]))

    return sample


def make_pixels(poly, sampler, classes, cols):
    minx, miny, maxx, maxy = poly.bounds
    width = maxx - minx
    height = maxy - miny
    cell = width / cols
    rows = math.ceil(height / cell)

    pixels = []
    for row in range(rows):
        for col in range(cols):
            cx0 = minx + col * cell
            cy0 = miny + row * cell
            full = box(cx0, cy0, cx0 + cell, cy0 + cell)
            if not full.intersects(poly):
                continue
            inset = cell * GAP_FRAC / 2
            shrunk = box(cx0 + inset, cy0 + inset, cx0 + cell - inset, cy0 + cell - inset)
            clipped = shrunk.intersection(poly)
            if clipped.is_empty:
                continue
            if clipped.area < (cell * cell) * MIN_COVERAGE * ((1 - GAP_FRAC) ** 2):
                continue
            value = sampler(full.centroid)
            pixels.append((clipped, classify(value, classes)))
    return pixels, (minx, miny, maxx, maxy)


def to_svg_paths(geom, scale, minx, maxy, decimals=2):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    paths = []
    for p in polys:
        rings = [p.exterior] + list(p.interiors)
        d_parts = []
        for ring in rings:
            pts = [
                f"{(lon - minx) * scale:.{decimals}f},{(maxy - lat) * scale:.{decimals}f}"
                for lon, lat in ring.coords
            ]
            d_parts.append("M" + "L".join(pts[:-1]) + " Z")
        paths.append(" ".join(d_parts))
    return paths


def render_svg(pixels, bounds, border_geom, out_path, viewbox_w=400, translate_y=None):
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny
    scale = viewbox_w / width
    viewbox_h = height * scale

    lines = []
    for geom, color in pixels:
        for d in to_svg_paths(geom, scale, minx, maxy):
            lines.append(f'  <path d="{d}" fill="{color}"/>')

    for d in to_svg_paths(border_geom, scale, minx, maxy):
        lines.append(
            f'  <path d="{d}" fill="none" stroke="{BORDER_COLOR}" '
            f'stroke-opacity="{BORDER_OPACITY}" stroke-width="{BORDER_WIDTH}" '
            f'stroke-linejoin="round"/>'
        )

    body = "\n".join(lines)
    if translate_y is not None:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w} {viewbox_w}">\n'
            f'  <g transform="translate(0,{translate_y:.2f})">\n{body}\n  </g>\n</svg>\n'
        )
    else:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w:.1f} {viewbox_h:.1f}">\n'
            f"{body}\n</svg>\n"
        )
    out_path.write_text(svg)
    print(f"wrote {out_path.relative_to(ROOT)} ({len(pixels)} pixels)")
    return viewbox_h


def render_favicon_ico(svg_path, out_path, sizes=FAVICON_ICO_SIZES):
    """Gera o favicon.ico (fallback para navegadores sem suporte a SVG) a
    partir do favicon.svg já renderizado, para os dois nunca ficarem
    dessincronizados."""
    frames = []
    for size in sizes:
        png_bytes = cairosvg.svg2png(url=str(svg_path), output_width=size, output_height=size)
        frames.append(Image.open(io.BytesIO(png_bytes)).convert("RGBA"))
    frames[-1].save(out_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[:-1])
    print(f"wrote {out_path.relative_to(ROOT)} ({len(sizes)} sizes)")


def main():
    poly, ivd = load_data()
    classes = load_classes()
    sampler = build_sampler(ivd)

    fine_pixels, fine_bounds = make_pixels(poly, sampler, classes, FINE_COLS)
    render_svg(fine_pixels, fine_bounds, poly, FINE_OUT)

    coarse_pixels, coarse_bounds = make_pixels(poly, sampler, classes, COARSE_COLS)
    vh = render_svg(coarse_pixels, coarse_bounds, poly, COARSE_OUT)

    translate_y = (400 - vh) / 2
    render_svg(coarse_pixels, coarse_bounds, poly, FAVICON_OUT, translate_y=translate_y)
    render_favicon_ico(FAVICON_OUT, FAVICON_ICO_OUT)


if __name__ == "__main__":
    main()
