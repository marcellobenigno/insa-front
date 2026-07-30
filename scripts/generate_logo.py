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

import cairocffi as cairo
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


# O wordmark usa texto SVG de verdade, na mesma pilha de fontes do corpo do
# site (`body { font-family }` em src/assets/base.css) — não mais uma fonte de
# pixel própria (ver histórico: uma grade 5×7 por glifo, imitando o mosaico do
# ícone). Trocado a pedido explícito do usuário: ele quer a marca com
# correspondência visual ao restante do site, não uma estética "retrô" que só
# o ícone tem. Usar a mesma lista de fontes (com os mesmos fallbacks) garante
# que, mesmo em visitantes fora do macOS/Safari (onde `-apple-system` e
# `BlinkMacSystemFont` não existem), a marca caia no mesmo fallback que o
# resto do texto do site cai para aquele visitante — ao contrário de
# converter o texto em contornos vetoriais fixos, que congelaria sempre a
# mesma fonte (a da máquina que rodou este script) e poderia destoar da fonte
# real exibida pelo navegador de quem acessa o site.
WORDMARK_TEXT_MAIN = "Desert"
WORDMARK_TEXT_ACCENT = "PB"
WORDMARK_FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
WORDMARK_FONT_WEIGHT = 700  # mesmo peso usado nos títulos mais proeminentes do site (ex. .feature-card h2)
WORDMARK_FONT_SIZE = 84
# "Desert" em preto (referência: logo pedida pelo usuário, desertpb.png).
# "PB" em vermelho — a pedido do usuário — usando o mesmo `#ff2424` do
# contorno de `limite_semiarido_pb` em styles.json ("Limite do Semiárido PB"):
# as letras "PB" (Paraíba) na mesma cor que desenha a fronteira da Paraíba no
# mapa, em vez de um vermelho arbitrário.
# Contorno branco grosso pintado atrás do preenchimento (`paint-order="stroke"`
# — sem isso, o traço fica centralizado no contorno da letra e "come" metade
# da própria tinta, afinando hastes finas) e uma sombra projetada
# (feDropShadow) garantem contraste contra qualquer fundo — nenhuma
# moldura/placa atrás do texto (foi tentado, ver "Jumbotron" no CLAUDE.md, e
# descartado). O SVG é estático (`<img>`), então isso precisa funcionar
# sozinho nos dois temas sem poder trocar de cor.
WORDMARK_COLOR = "#000000"
WORDMARK_ACCENT_COLOR = "#ff2424"
WORDMARK_STROKE = "#ffffff"
WORDMARK_STROKE_WIDTH = 3
WORDMARK_VGAP = 14  # espaço entre a base do ícone e o topo da área do texto
# Área reservada para o texto — generosa o bastante pra caber "DesertPB" em
# negrito em qualquer uma das fontes do fallback acima sem cortar (a largura
# real varia por fonte/plataforma; texto SVG não dá pra medir com exatidão em
# tempo de geração, e um <img> sempre recorta no viewBox, sem "overflow:
# visible" — por isso a margem de segurança, calibrada visualmente).
WORDMARK_CANVAS_W = 430
WORDMARK_CANVAS_H = 92
# Fonte de referência só pra medir a largura do texto (ver `measure_text_width`
# abaixo) — não precisa ser a mesma do `WORDMARK_FONT_FAMILY` renderizado no
# navegador, só uma fonte bold sans-serif real e comum o bastante pra existir
# na máquina que roda o gerador.
WORDMARK_MEASURE_FONT = "Arial"


def measure_text_width(text, font_size, font=WORDMARK_MEASURE_FONT):
    """Largura (avanço horizontal) de `text` em unidades do SVG, via
    `cairo.Context.text_extents` — não dá pra confiar em `text-anchor="middle"`
    com <tspan> multi-cor em todo renderizador de SVG (o cairosvg usado neste
    script, por exemplo, não posiciona esse caso corretamente, deslocando o
    tspan pra fora da tela) então "Desert" + "PB" são centralizados na mão
    com `text-anchor="start"` a partir dessa medida — sem a ambiguidade de
    onde cada "text chunk" deveria ser ancorado."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    ctx = cairo.Context(surface)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    return ctx.text_extents(text)[4]  # x_advance


def render_lockup_svg(pixels, bounds, border_geom, out_path, icon_w=400):
    """Ícone + wordmark "DesertPB" empilhados verticalmente, como uma única
    marca — para uso onde o nome deve aparecer junto ao ícone sem depender de
    texto HTML ao lado (ex.: cabeçalho da SobreView).

    O canvas final é mais largo que o ícone só quando o texto precisa de mais
    espaço — o ícone em si sempre renderiza em `icon_w`, centralizado por um
    `translate`, sem distorcer a silhueta real."""
    icon_body, icon_h = build_icon_body(pixels, bounds, border_geom, icon_w)

    viewbox_w = max(icon_w, WORDMARK_CANVAS_W)
    icon_x = (viewbox_w - icon_w) / 2
    text_y0 = icon_h + WORDMARK_VGAP
    viewbox_h = text_y0 + WORDMARK_CANVAS_H

    text_w = measure_text_width(WORDMARK_TEXT_MAIN + WORDMARK_TEXT_ACCENT, WORDMARK_FONT_SIZE)
    text_x0 = (viewbox_w - text_w) / 2

    text = (
        f'  <text x="{text_x0:.2f}" y="{text_y0 + WORDMARK_CANVAS_H / 2:.2f}" '
        f'text-anchor="start" dominant-baseline="central" '
        f'font-family="{WORDMARK_FONT_FAMILY}" font-weight="{WORDMARK_FONT_WEIGHT}" '
        f'font-size="{WORDMARK_FONT_SIZE}" '
        f'fill="{WORDMARK_COLOR}" stroke="{WORDMARK_STROKE}" stroke-width="{WORDMARK_STROKE_WIDTH}" '
        f'paint-order="stroke">{WORDMARK_TEXT_MAIN}'
        f'<tspan fill="{WORDMARK_ACCENT_COLOR}">{WORDMARK_TEXT_ACCENT}</tspan></text>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewbox_w:.1f} {viewbox_h:.1f}">\n'
        f"  <defs>\n"
        f'    <filter id="wordmark-shadow" x="-30%" y="-30%" width="160%" height="160%">\n'
        f'      <feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.55"/>\n'
        f"    </filter>\n"
        f"  </defs>\n"
        f'  <g transform="translate({icon_x:.2f},0)">\n{icon_body}\n  </g>\n'
        f'  <g filter="url(#wordmark-shadow)">\n{text}\n  </g>\n</svg>\n'
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
