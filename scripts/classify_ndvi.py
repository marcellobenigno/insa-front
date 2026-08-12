"""
Classifica o raster de NDVI em 6 tipos de vegetação/cobertura do solo e
converte o resultado para vetor, usando o pipeline padrão do GDAL:

  1. Reclassificação (NDVI contínuo -> código de classe 1-6), via GDAL/numpy
  2. gdal_sieve.py    -- remove manchas de ruído (clusters pequenos demais
                          pra serem uma classe real) antes de vetorizar
  3. gdal_polygonize.py -- rasteriza -> vetor (1 polígono por cluster de
                          pixels conectados com a mesma classe)
  4. Dissolve por classe (geopandas) + junção dos metadados de cada classe

Tabela de classificação (mesmos limiares/pesos já usados em
src/assets/styles.json, camada "ndvi", campo "peso"):

  Tipo de vegetação                          NDVI
  Arbórea muito densa                        >= 0.617
  Arbórea densa / Subarbórea                 0.484 - 0.617
  Subarbustiva muito densa / Subarbórea      0.425 - 0.484
  Arbustiva aberta / Subarbórea              0.296 - 0.425
  Subarbustiva muito rala / Arbustiva        0.254 - 0.296
  Solo exposto / Gramíneas herbáceas         0 - 0.254

Rodar da raiz do projeto:

  python scripts/classify_ndvi.py

Saídas (na mesma pasta do raster de origem):
  NDVI_MAIO_2022_classe.tif     -- raster reclassificado (1-6) e limpo pelo sieve
  NDVI_MAIO_2022_otimizado.shp  -- vetor final, uma feição (multipolígono) por classe

O campo "classe" do vetor final é uma string composta ("1 - Arbórea muito
densa (≥ 0.617)", etc.) que bate byte-a-byte com as <category value=...> do
QML de ndvi_maio salvo em layer_styles no GeoPackage (categorizedSymbol,
attr="classe") -- é esse campo que styles.py extrai automaticamente pra
simbologia/legenda/popup no app, não "peso". O código numérico 1-6 vai à
parte em "classe_num".
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from osgeo import gdal

sys.path.insert(0, str(Path(__file__).parent))
from geo_utils import TARGET_CRS, fix_geometries  # noqa: E402

gdal.UseExceptions()

BASE_DIR = Path(__file__).parent.parent
NDVI_DIR = (
    BASE_DIR
    / "data"
    / "Indicadores de Vulnerabilidade"
    / "Indicadores de Vegetação"
    / "NDVI"
)

SRC_TIF = NDVI_DIR / "NDVI_MAIO_2022.tif"
CLASSE_TIF = NDVI_DIR / "NDVI_MAIO_2022_classe.tif"
VECTOR_SHP = NDVI_DIR / "NDVI_MAIO_2022_otimizado.shp"

# Limiar do gdal_sieve, em nº de pixels conectados (remove clusters com
# tamanho < threshold, fundindo-os na classe vizinha dominante).
#
# As classes raras (3, 5, 6) são naturalmente fragmentadas — muitos clusters
# de 1 único pixel espalhados pelo território (ruído típico de classificação
# por limiar sobre um índice contínuo, nas bordas entre faixas de NDVI), não
# concentrados numa mancha só. Isso foi medido empiricamente: subir o limiar
# de 2 para 8 px já derruba a área da classe 3 em ~47% e da classe 5 em
# ~75%, porque cada cluster isolado dessas classes tem poucos pixels e é
# fundido inteiro na classe 1/2/4 vizinha. Por isso o limiar fica no mínimo
# que ainda faz sentido como "sieve" (remove só ilhas de 1 pixel — ruído
# sal-e-pimenta puro) em vez de um valor maior "redondo" — qualquer limiar
# maior teria um viés sistemático contra as classes menos comuns, não é só
# uma questão de remover mais ruído.
SIEVE_THRESHOLD_PX = 2

# classe_num (1 = maior vigor vegetativo) -> metadados. Faixas/pesos/rótulos
# de vulnerabilidade na mesma convenção de src/assets/styles.json (camada
# "ndvi"), pra este vetor já nascer compatível com o resto do pipeline.
CLASSES = [
    {
        "classe_num": 1,
        "tipo_veget": "Arbórea muito densa",
        "ndvi_min": 0.617,
        "ndvi_max": None,
        "ndvi_faixa": "≥ 0.617",
        "classe_lbl": "Muito Baixa",
        "peso": 1.0,
    },
    {
        "classe_num": 2,
        "tipo_veget": "Arbórea densa / Subarbórea",
        "ndvi_min": 0.484,
        "ndvi_max": 0.617,
        "ndvi_faixa": "0.484 – 0.617",
        "classe_lbl": "Baixa",
        "peso": 1.1,
    },
    {
        "classe_num": 3,
        "tipo_veget": "Subarbustiva muito densa / Subarbórea",
        "ndvi_min": 0.425,
        "ndvi_max": 0.484,
        "ndvi_faixa": "0.425 – 0.484",
        "classe_lbl": "Moderada",
        "peso": 1.3,
    },
    {
        "classe_num": 4,
        "tipo_veget": "Arbustiva aberta / Subarbórea",
        "ndvi_min": 0.296,
        "ndvi_max": 0.425,
        "ndvi_faixa": "0.296 – 0.425",
        "classe_lbl": "Moderada-Alta",
        "peso": 1.5,
    },
    {
        "classe_num": 5,
        "tipo_veget": "Subarbustiva muito rala / Arbustiva",
        "ndvi_min": 0.254,
        "ndvi_max": 0.296,
        "ndvi_faixa": "0.254 – 0.296",
        "classe_lbl": "Alta",
        "peso": 1.8,
    },
    {
        "classe_num": 6,
        "tipo_veget": "Solo exposto / Gramíneas herbáceas",
        "ndvi_min": 0.0,
        "ndvi_max": 0.254,
        "ndvi_faixa": "0 – 0.254",
        "classe_lbl": "Muito Alta",
        "peso": 2.0,
    },
]

# "classe" (string) precisa bater byte-a-byte com os `value`/`label` das
# <category> do QML salvo em layer_styles para ndvi_maio (categorizedSymbol,
# attr="classe") — é esse campo, não "peso", que dirige a simbologia/legenda/
# popup no app. "classe_num" (o código de pixel 1-6) fica como campo à parte
# só pra join/ordenação internos.
for _c in CLASSES:
    _c["classe"] = f"{_c['classe_num']} - {_c['tipo_veget']} ({_c['ndvi_faixa']})"

# Limiares ascendentes (edges de np.digitize) usados pra decidir a classe de
# cada pixel — mesma convenção "graduated" (bound superior) do resto do app
# (ver classify_graduated em geo_utils.py / mapRenderer.js).
_EDGES = [0.254, 0.296, 0.425, 0.484, 0.617]


def reclassify(src_path, dst_path):
    """Lê o NDVI contínuo e grava um raster Byte com o código de classe
    (1-6) de cada pixel, nodata=0."""
    ds = gdal.Open(str(src_path))
    band = ds.GetRasterBand(1)
    raw = band.ReadAsArray().astype(np.float64)

    # O raster de origem cobre um retângulo (bounding box) maior que o
    # contorno irregular do Semiárido PB (silhueta bilobada) — os pixels
    # fora do polígono real vêm preenchidos com 0.0 exato (não é um NDVI
    # real; ~48% do raster). Índices NDVI computados nunca caem em 0.0
    # exato com essa frequência (todo outro valor do raster é uma decimal
    # "ruidosa" distinta, típica de reflectância real), então 0.0 aqui é
    # tratado como nodata/fora-da-área, não como classe 6 — do contrário
    # a classe "Solo exposto" ficaria contaminada com a área inteira fora
    # do Semiárido. Os poucos pixels negativos (~20, provavelmente água/
    # sombra) também ficam fora da tabela de classificação (que começa em
    # 0) e são igualmente tratados como nodata.
    valid = raw > 0

    idx = np.digitize(raw, _EDGES, right=True)  # 0..5, ascendente por NDVI
    class_code = (6 - idx).astype(np.uint8)
    class_code[~valid] = 0

    driver = gdal.GetDriverByName("GTiff")
    out = driver.Create(
        str(dst_path),
        ds.RasterXSize,
        ds.RasterYSize,
        1,
        gdal.GDT_Byte,
        options=["COMPRESS=LZW"],
    )
    out.SetGeoTransform(ds.GetGeoTransform())
    out.SetProjection(ds.GetProjection())
    out_band = out.GetRasterBand(1)
    out_band.WriteArray(class_code)
    out_band.SetNoDataValue(0)
    out_band.FlushCache()
    out = None
    ds = None


def sieve(path, threshold_px):
    """Remove clusters de pixels menores que threshold_px (funde na classe
    vizinha dominante), respeitando o nodata do próprio raster."""
    subprocess.run(
        [
            "gdal_sieve.py",
            "-st",
            str(threshold_px),
            "-8",
            str(path),
        ],
        check=True,
    )


def polygonize(src_path, dst_shp):
    """Vetoriza o raster classificado (1 polígono por cluster de pixels
    conectados com a mesma classe); pixels nodata são pulados automaticamente
    (gdal_polygonize usa o próprio nodata da banda como máscara por padrão)."""
    subprocess.run(
        [
            "gdal_polygonize.py",
            "-8",
            str(src_path),
            "-f",
            "ESRI Shapefile",
            str(dst_shp),
            "ndvi_raw",
            "classe_num",
        ],
        check=True,
    )


def dissolve_and_enrich(raw_shp):
    gdf = gpd.read_file(raw_shp)
    gdf = gdf[gdf["classe_num"] > 0]  # segurança extra: descarta nodata se sobrar algo

    dissolved = gdf.dissolve(by="classe_num", as_index=False)
    dissolved = fix_geometries(dissolved)

    meta = pd.DataFrame(CLASSES)
    merged = dissolved.merge(meta, on="classe_num", how="left")
    merged = merged[
        ["classe", "classe_num", "tipo_veget", "ndvi_min", "ndvi_max", "ndvi_faixa", "classe_lbl", "peso", "geometry"]
    ]
    return merged.sort_values("classe_num").reset_index(drop=True)


def print_summary(gdf):
    areas = gdf.to_crs(TARGET_CRS).geometry.area / 1e6  # km²
    print("\nResumo por classe:")
    for (_, row), area_km2 in zip(gdf.iterrows(), areas):
        print(
            f"  {row['classe_num']}  {row['tipo_veget']:<40} "
            f"{row['ndvi_faixa']:<16} {area_km2:>10.1f} km²  (peso {row['peso']})"
        )
    print(f"  Total: {areas.sum():.1f} km²\n")


def remove_shp(path):
    for ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
        p = path.with_suffix(ext)
        if p.exists():
            p.unlink()


def main():
    if not SRC_TIF.exists():
        sys.exit(f"Raster não encontrado: {SRC_TIF}")

    print(f"1/4 Reclassificando {SRC_TIF.name} -> {CLASSE_TIF.name}")
    reclassify(SRC_TIF, CLASSE_TIF)

    print(f"2/4 gdal_sieve (limiar {SIEVE_THRESHOLD_PX} px)")
    sieve(CLASSE_TIF, SIEVE_THRESHOLD_PX)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_shp = Path(tmp) / "ndvi_raw.shp"
        print("3/4 gdal_polygonize")
        polygonize(CLASSE_TIF, tmp_shp)

        print("4/4 Dissolve por classe + metadados")
        final_gdf = dissolve_and_enrich(tmp_shp)

    remove_shp(VECTOR_SHP)
    final_gdf.to_file(VECTOR_SHP, driver="ESRI Shapefile")

    print(f"\nRaster classificado: {CLASSE_TIF}")
    print(f"Vetor final:         {VECTOR_SHP} ({len(final_gdf)} feições)")
    print_summary(final_gdf)


if __name__ == "__main__":
    main()
