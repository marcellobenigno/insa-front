# Adicionar nova camada ao insa-front

Vou te guiar pelo processo completo de adição de uma nova camada.
Preciso das seguintes informações antes de começar:

1. **Nome exato da camada no GeoPackage** (rode `ogrinfo -q data/dados_insa.gpkg` se não souber)
2. **Categoria** onde ela deve aparecer na sidebar (leia `src/config/layers.js` para ver as categorias existentes)
3. **Label** para exibição no menu
4. **Descrição curta** (campo `meta`)
5. **Campos disponíveis** na camada (rode `ogrinfo -al -so data/dados_insa.gpkg <nome_camada>`)
6. **A camada é stroke-only** (só borda, sem preenchimento) ou tem fill?

Com essas informações, vou:

## Parte 1 — Pipeline de dados

Verificar se o GeoJSON já existe em `data/geojson/`. Se não existir, gerar (da raiz do projeto):

```bash
ogr2ogr -f GeoJSON data/geojson/<nome_camada>.geojson \
  data/dados_insa.gpkg <nome_camada> \
  -t_srs EPSG:4326
```

Adicionar o novo GeoJSON ao comando Tippecanoe existente no CLAUDE.md e regenerar os tiles:

```bash
tippecanoe \
  -o data/mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  [todos os data/geojson/*.geojson existentes + o novo]

rm -rf public/tiles/insa_layers
python scripts/export.py
python scripts/styles.py
python scripts/stats.py
```

Se a camada for stroke-only, adicionar manualmente em `src/assets/styles.json`:
```json
"<nome_camada>": {
  "Rótulo legenda": "stroke:#ffffff"
}
```

## Parte 2 — Código

Adicionar o objeto da camada em `src/config/layers.js` na categoria correta:

```js
<nome_chave>: {
  label: '<label>',
  meta: '<descrição curta>',
  url: VECTOR_TILES_URL,
  sourceLayer: '<nome_exato_no_gpkg>',
  zIndex: <valor conforme convenção>,
  active: false,
  searchFields: [<campos identificadores>],
  fieldTypes: { <campo>: 'string' | 'number' },
  popUpFields: [<campos para o popup>],
  descFields: { <campo>: '<rótulo amigável>' },
},
```

Verificar se há campos novos não listados em `src/utils/mapRenderer.js → possibleValues`
e adicioná-los se necessário.

## Parte 3 — Verificação

Rodar o servidor de desenvolvimento e confirmar visualmente:
- A camada aparece na categoria correta na sidebar
- Os tiles renderizam no mapa
- O popup exibe os campos corretos
- A legenda aparece no LayerCard

```bash
npm run dev
```

## Parte 4 — Atualizar CLAUDE.md

Adicionar a nova camada na tabela de camadas existentes do `CLAUDE.md`
e atualizar o comando Tippecanoe com o novo GeoJSON.
