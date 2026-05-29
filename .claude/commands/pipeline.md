# Regenerar pipeline de vector tiles

Executa o pipeline completo: GeoPackage → GeoJSON → MBTiles → PBF → styles.json

> ⚠️ Use este comando sempre que o GeoPackage (`data/dados_insa.gpkg`) for alterado.
> Não existe atualização parcial — o pipeline sempre roda do zero.
> Todos os comandos rodam da **raiz do projeto**.

## Passo 1 — Verificar quais camadas existem no GeoPackage

```bash
ogrinfo -q data/dados_insa.gpkg
```

Comparar com a lista de GeoJSONs em `data/geojson/` e com as camadas no CLAUDE.md.
Reportar qualquer divergência antes de continuar.

## Passo 2 — Exportar camadas para GeoJSON

Para cada camada listada no GeoPackage que ainda não tenha GeoJSON correspondente:

```bash
ogr2ogr -f GeoJSON data/geojson/<nome_camada>.geojson \
  data/dados_insa.gpkg <nome_camada> \
  -t_srs EPSG:4326
```

## Passo 3 — Gerar MBTiles com Tippecanoe

```bash
tippecanoe \
  -o data/mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  data/geojson/declividade_sab_pb_original.geojson \
  data/geojson/declividade_sab_pb_pesos.geojson \
  data/geojson/eto_sab_pb_original.geojson \
  data/geojson/eto_sab_pb_pesos.geojson \
  data/geojson/geologia_sab_pb_original.geojson \
  data/geojson/geologia_sab_pb_pesos.geojson \
  data/geojson/ia_sab_pb_original.geojson \
  data/geojson/ia_sab_pb_pesos.geojson \
  data/geojson/iqc_sab_pb.geojson \
  data/geojson/iqs_sab_pb.geojson \
  data/geojson/layer_styles.geojson \
  data/geojson/municipios_pb_semiarido.geojson \
  data/geojson/precipitacao_sab_pb_original.geojson \
  data/geojson/precipitacao_sab_pb_pesos.geojson \
  data/geojson/solos_tipos_sab_pb_original.geojson \
  data/geojson/solos_tipos_sab_pb_pesos.geojson \
  data/geojson/textura_sab_pb_original.geojson \
  data/geojson/textura_sab_pb_pesos.geojson
```

Reportar o tamanho do `.mbtiles` gerado. Esperado: ~90 MB.

## Passo 4 — Deletar tiles antigos e reextrair

```bash
rm -rf public/tiles/insa_layers
python scripts/export.py
```

Confirmar que `public/tiles/insa_layers/` foi recriado com subdiretórios `{z}/{x}/{y}.pbf`.

## Passo 5 — Reextrair estilos

```bash
python scripts/styles.py
```

Abrir `src/assets/styles.json` e verificar se todas as camadas esperadas estão presentes.
Reportar quais estão ausentes (provavelmente stroke-only no QGIS).
Restaurar entradas manuais (ver seção "manual entries" no CLAUDE.md).

## Passo 6 — Regenerar estatísticas

```bash
python scripts/stats.py
```

Confirmar que `src/assets/stats.json` foi atualizado com as classes corretas.

## Passo 7 — Verificação final

```bash
npm run dev
```

Confirmar no browser que os tiles carregam corretamente para pelo menos uma camada de cada categoria.
