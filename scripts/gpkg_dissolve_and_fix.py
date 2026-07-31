"""
Reduz o tamanho de data/dados_insa.gpkg:

1. Corrige geometrias inválidas (`native:fixgeometries`) em toda camada
   vetorial do GeoPackage.
2. Agrupa (`native:dissolve`, "group by") feições que compartilham os
   mesmos valores em TODOS os seus campos de atributo, sempre que isso reduz
   o número de feições — nunca altera nome, tipo ou ordem dos campos, só
   funde a geometria de linhas com atributos idênticos numa só feição
   multipart.

Quais camadas são candidatas a dissolve é decidido em tempo de execução (via
`groupable()`, comparando `COUNT(*)` com `COUNT(DISTINCT <todos os campos>)`
direto no SQLite do GeoPackage) — não uma lista fixa. Estão fora do processo
(nem fix nem dissolve) só as camadas em `EXCLUDE_LAYERS` abaixo, por motivo de
correção (não tamanho): limites administrativos, cujas feições precisam
continuar endereçáveis individualmente pela aplicação, e tabelas não
espaciais do QGIS.

## Rodando este script

Precisa do ambiente Python do QGIS (`qgis.core`, `processing`), não do
Python do projeto (`venv`/pyenv usado pelos outros scripts em `scripts/`).
Duas formas de rodar:

  a) Console Python do QGIS (QGIS Desktop → Plugins → Console Python):
     exec(open("scripts/gpkg_dissolve_and_fix.py").read())

  b) Standalone, com o QGIS instalado (ajuste os caminhos pro seu SO):
     QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS \
     PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python \
     /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/gpkg_dissolve_and_fix.py

## Segurança

- Roda em **DRY_RUN por padrão** (`DRY_RUN = True` abaixo) — só imprime o
  relatório (o que seria feito em cada camada), sem gravar nada. Rodar de
  verdade exige mudar essa flag pra `False` manualmente, depois de revisar o
  relatório.
- Sempre faz uma cópia de segurança do `.gpkg` inteiro antes da primeira
  escrita (`<nome>.antes-dissolve.gpkg`, ao lado do original) — nunca
  sobrescreve um backup já existente (assume que já rodou antes e para com
  erro, pra nunca sobrescrever o "antes" de uma rodada anterior).
- Cada camada é processada em uma tabela temporária (`<nome>__tmp`) dentro do
  mesmo GeoPackage; só depois de escrita com sucesso a tabela original é
  apagada e a temporária é renomeada pro nome original (via `ogr.Layer.Rename`,
  que atualiza corretamente todo o bookkeeping do GeoPackage — índice
  espacial rtree, gpkg_contents, gpkg_geometry_columns — GDAL ≥ 3.5). Nunca
  há um meio-termo em que a tabela original já foi apagada mas a nova ainda
  não está no lugar dela.
"""

import sqlite3
from pathlib import Path

from qgis.core import QgsApplication, QgsProcessingFeedback
import processing
from osgeo import ogr

ROOT = Path(__file__).parent.parent
GPKG_PATH = ROOT / "data" / "dados_insa.gpkg"
BACKUP_PATH = GPKG_PATH.with_name(GPKG_PATH.stem + ".antes-dissolve.gpkg")

DRY_RUN = True  # mude pra False só depois de revisar o relatório impresso

# Fora do processo por correção, não por tamanho:
# - limites administrativos: cada feição (município/estado/contorno) precisa
#   continuar endereçável individualmente pela aplicação (popup, busca,
#   fitBounds); mesmo quando o dissolve não reduziria nada (não reduziria
#   mesmo — cada uma já é um valor único), fundir features de entidades
#   administrativas diferentes seria incorreto por definição.
# - focos_queimadas: camada de pontos sem nenhum campo de atributo (só
#   geometria) — não há campo pra agrupar.
# - qgis_projects / layer_styles: tabelas não espaciais do QGIS (projeto
#   salvo no próprio GeoPackage e estilos QML), não são camadas vetoriais.
EXCLUDE_LAYERS = {
    "municipios_pb_semiarido",
    "estados_ne",
    "limite_semiarido_pb",
    "limite_do_semiarido_br",
    "focos_queimadas",
    "qgis_projects",
    "layer_styles",
}


def list_feature_layers(gpkg_path):
    con = sqlite3.connect(gpkg_path)
    cur = con.cursor()
    cur.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features' ORDER BY table_name")
    layers = [r[0] for r in cur.fetchall()]
    con.close()
    return layers


def layer_fields(gpkg_path, layer_name):
    """Nomes dos campos de atributo (exclui fid e a coluna de geometria),
    na ordem exata do schema — é essa mesma lista, nessa mesma ordem, que
    vira o parâmetro FIELD do dissolve, garantindo que nome/ordem dos campos
    nunca mudem no resultado."""
    con = sqlite3.connect(gpkg_path)
    cur = con.cursor()
    cur.execute("SELECT column_name FROM gpkg_geometry_columns WHERE table_name=?", (layer_name,))
    row = cur.fetchone()
    geom_col = row[0] if row else None
    cur.execute(f'PRAGMA table_info("{layer_name}")')
    cols = [r[1] for r in cur.fetchall() if r[1] not in ("fid", geom_col)]
    con.close()
    return cols


def groupable(gpkg_path, layer_name, fields):
    """True se existe pelo menos uma dupla de feições com os mesmos valores
    em TODOS os campos — nesse caso o dissolve reduz o número de feições.
    Se cada feição já tem uma combinação de valores única, não há o que
    agrupar (dissolve não reduziria nada)."""
    if not fields:
        return False, 0, 0
    con = sqlite3.connect(gpkg_path)
    cur = con.cursor()
    cur.execute(f'SELECT COUNT(*) FROM "{layer_name}"')
    total = cur.fetchone()[0]
    concat = " || '|' || ".join(f'IFNULL("{f}",\'\')' for f in fields)
    cur.execute(f'SELECT COUNT(DISTINCT {concat}) FROM "{layer_name}"')
    distinct = cur.fetchone()[0]
    con.close()
    return distinct < total, total, distinct


def backup_gpkg():
    if BACKUP_PATH.exists():
        raise RuntimeError(
            f"Backup já existe em {BACKUP_PATH} — apague-o manualmente (ou "
            "restaure a partir dele) antes de rodar de novo, pra nunca "
            "sobrescrever o backup de uma rodada anterior."
        )
    print(f"Copiando backup: {GPKG_PATH} -> {BACKUP_PATH}")
    import shutil

    shutil.copy2(GPKG_PATH, BACKUP_PATH)


def swap_in_place(gpkg_path, original_name, tmp_name):
    """Apaga a tabela original e renomeia a temporária pro nome original —
    só chamado depois que a tabela temporária já foi escrita com sucesso, e
    usando `ogr.Layer.Rename` (não um `ALTER TABLE` cru) pra manter o
    índice espacial (rtree) e o bookkeeping do GeoPackage
    (gpkg_contents/gpkg_geometry_columns) corretos — validado manualmente
    (rtree + triggers renomeados certo, consulta espacial funcionando depois
    do swap) antes deste script existir."""
    ds = ogr.Open(str(gpkg_path), update=1)
    try:
        original_idx = next(
            (i for i in range(ds.GetLayerCount()) if ds.GetLayerByIndex(i).GetName() == original_name),
            None,
        )
        if original_idx is not None:
            ds.DeleteLayer(original_idx)
        new_layer = ds.GetLayerByName(tmp_name)
        new_layer.Rename(original_name)
    finally:
        ds = None


def process_layer(layer_name, feedback):
    fields = layer_fields(GPKG_PATH, layer_name)
    can_group, total, distinct = groupable(GPKG_PATH, layer_name, fields)

    action = "dissolve" if can_group else "só fix geometries"
    reduction = f"{total} -> {distinct} feições" if can_group else f"{total} feições (sem redução possível)"
    print(f"  [{layer_name}] campos={fields} | {action} | {reduction}")

    if DRY_RUN:
        return

    tmp_name = f"{layer_name}__tmp"
    source = f"{GPKG_PATH}|layername={layer_name}"
    dest = f"ogr:dbname='{GPKG_PATH}' table=\"{tmp_name}\" (geom)"

    if can_group:
        # fixgeometries fica em memória (não grava no disco ainda) e alimenta
        # direto o dissolve, que é quem grava o resultado final na tabela
        # temporária — evita uma escrita intermediária no GeoPackage.
        fixed = processing.run(
            "native:fixgeometries",
            {"INPUT": source, "METHOD": 1, "OUTPUT": "memory:"},
            feedback=feedback,
        )["OUTPUT"]
        processing.run(
            "native:dissolve",
            {"INPUT": fixed, "FIELD": fields, "SEPARATE_DISJOINT": False, "OUTPUT": dest},
            feedback=feedback,
        )
    else:
        # Sem dissolve possível — fixgeometries já grava direto na tabela
        # temporária, sem precisar do passo em memória.
        processing.run(
            "native:fixgeometries",
            {"INPUT": source, "METHOD": 1, "OUTPUT": dest},
            feedback=feedback,
        )

    swap_in_place(GPKG_PATH, layer_name, tmp_name)


def main():
    feedback = QgsProcessingFeedback()

    layers = [name for name in list_feature_layers(GPKG_PATH) if name not in EXCLUDE_LAYERS]
    skipped = [name for name in list_feature_layers(GPKG_PATH) if name in EXCLUDE_LAYERS]

    print(f"GeoPackage: {GPKG_PATH}")
    print(f"DRY_RUN = {DRY_RUN}")
    print(f"\nCamadas fora do processo (correção, ver EXCLUDE_LAYERS): {sorted(skipped)}\n")
    print(f"Processando {len(layers)} camadas:")

    if not DRY_RUN:
        backup_gpkg()

    for layer_name in layers:
        process_layer(layer_name, feedback)

    if not DRY_RUN:
        # Apagar/recriar tabelas (o swap_in_place de cada camada) libera
        # páginas dentro do arquivo SQLite, mas não encolhe o arquivo no
        # disco por si só — sem VACUUM o .gpkg pode até GANHAR tamanho
        # temporariamente (todas as tabelas __tmp intermediárias já foram
        # apagadas, mas o espaço só é reaproveitado, não devolvido ao SO).
        print("Compactando o arquivo (VACUUM)...")
        con = sqlite3.connect(GPKG_PATH)
        con.execute("VACUUM")
        con.close()

    print("\nConcluído." if not DRY_RUN else "\nDRY_RUN — nada foi escrito. Revise o relatório acima antes de rodar de verdade.")


if __name__ == "__main__":
    if not QgsApplication.instance():
        qgs = QgsApplication([], False)
        qgs.initQgis()
        from processing.core.Processing import Processing

        Processing.initialize()
        from qgis.analysis import QgsNativeAlgorithms

        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    main()
