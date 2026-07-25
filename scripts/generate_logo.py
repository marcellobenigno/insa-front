"""
Gera a marca DesertPB (src/assets/logo-mark-fine.svg, logo-mark-coarse.svg,
logo-lockup.svg, public/favicon.svg e public/favicon.ico) a partir do
contorno real de limite_semiarido_pb.

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
LOCKUP_FINE_OUT = ROOT / "src" / "assets" / "logo-lockup-fine.svg"
LOCKUP_COARSE_OUT = ROOT / "src" / "assets" / "logo-lockup-coarse.svg"
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


def build_icon_body(pixels, bounds, border_geom, viewbox_w=400):
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

    return "\n".join(lines), viewbox_h


def render_svg(pixels, bounds, border_geom, out_path, viewbox_w=400, translate_y=None):
    body, viewbox_h = build_icon_body(pixels, bounds, border_geom, viewbox_w)
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


# Fonte de pixel própria (grade 5×7 por glifo), pra combinar com a estética
# de blocos do mosaico — uma fonte lisa (system-ui) destoava demais do resto
# da marca. Maiúsculas apenas (pixel font clássica de 8-bit).
WORDMARK_GLYPHS = {
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "R": ["####.", "#...#", "#...#", "####.", "#..#.", "#...#", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
}
GLYPH_W = 5
GLYPH_H = 7
GLYPH_GAP_COLS = 1

WORDMARK_WORD = "DESERTPB"
# Preto uniforme em todas as letras (referência: logo pedida pelo usuário,
# desertpb.png) — nada de dividir a cor por palavra. Contorno branco grosso
# em vez de sutil, e uma sombra projetada (feDropShadow) fazem o contraste
# contra a foto, no lugar de uma moldura/placa atrás do texto.
WORDMARK_COLOR = "#000000"
WORDMARK_STROKE = "#ffffff"
WORDMARK_CELL = 8.1
WORDMARK_GAP_FRAC = 0.16
WORDMARK_VGAP = 6  # espaço entre a base do ícone e o topo do texto


def render_lockup_svg(pixels, bounds, border_geom, out_path, icon_w=400):
    """Ícone + wordmark "DESERTPB" empilhados verticalmente, em pixel font,
    como uma única marca — para uso onde o nome deve aparecer junto ao ícone
    sem depender de texto HTML ao lado (ex.: cabeçalho da SobreView).

    O canvas final é mais largo que o ícone só quando o texto precisa de mais
    espaço — o ícone em si sempre renderiza em `icon_w`, centralizado por um
    `translate`, sem distorcer a silhueta real."""
    icon_body, icon_h = build_icon_body(pixels, bounds, border_geom, icon_w)

    cols_per_glyph = GLYPH_W + GLYPH_GAP_COLS
    total_cols = len(WORDMARK_WORD) * cols_per_glyph - GLYPH_GAP_COLS
    text_w = total_cols * WORDMARK_CELL
    text_h = GLYPH_H * WORDMARK_CELL

    viewbox_w = max(icon_w, text_w)
    icon_x = (viewbox_w - icon_w) / 2
    text_x0 = (viewbox_w - text_w) / 2
    text_y0 = icon_h + WORDMARK_VGAP
    viewbox_h = text_y0 + text_h

    rects = []
    for i, ch in enumerate(WORDMARK_WORD):
        col_offset = i * cols_per_glyph
        for row, line in enumerate(WORDMARK_GLYPHS[ch]):
            for col, bit in enumerate(line):
                if bit != "#":
                    continue
                inset = WORDMARK_CELL * WORDMARK_GAP_FRAC / 2
                x = text_x0 + (col_offset + col) * WORDMARK_CELL + inset
                y = text_y0 + row * WORDMARK_CELL + inset
                size = WORDMARK_CELL - inset * 2
                rects.append(
                    f'  <rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" '
                    f'fill="{WORDMARK_COLOR}" stroke="{WORDMARK_STROKE}" stroke-width="1"/>'
                )
    text_body = "\n".join(rects)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w:.1f} {viewbox_h:.1f}">\n'
        f"  <defs>\n"
        f'    <filter id="wordmark-shadow" x="-30%" y="-30%" width="160%" height="160%">\n'
        f'      <feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.55"/>\n'
        f"    </filter>\n"
        f"  </defs>\n"
        f'  <g transform="translate({icon_x:.2f},0)">\n{icon_body}\n  </g>\n'
        f'  <g filter="url(#wordmark-shadow)">\n{text_body}\n  </g>\n</svg>\n'
    )
    out_path.write_text(svg)
    print(f"wrote {out_path.relative_to(ROOT)} (ícone + wordmark)")


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
    render_lockup_svg(fine_pixels, fine_bounds, poly, LOCKUP_FINE_OUT)

    coarse_pixels, coarse_bounds = make_pixels(poly, sampler, classes, COARSE_COLS)
    vh = render_svg(coarse_pixels, coarse_bounds, poly, COARSE_OUT)

    render_lockup_svg(coarse_pixels, coarse_bounds, poly, LOCKUP_COARSE_OUT)

    translate_y = (400 - vh) / 2
    render_svg(coarse_pixels, coarse_bounds, poly, FAVICON_OUT, translate_y=translate_y)
    render_favicon_ico(FAVICON_OUT, FAVICON_ICO_OUT)


if __name__ == "__main__":
    main()
