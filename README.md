# INSA Front

Aplicação web de mapeamento GIS desenvolvida com Vue 3 + Vite. Exibe camadas vetoriais do INSA sobre um mapa base interativo (OpenStreetMap ou ESRI Satellite), com suporte a vector tiles locais e legendas dinâmicas por camada.

## Pré-requisitos

- **Node.js** `^20.19.0` ou `>=22.12.0`

## Instalação e execução

```sh
npm install
npm run dev       # servidor de desenvolvimento com hot-reload
npm run build     # build de produção em dist/
npm run preview   # preview do build de produção
```

## Comandos disponíveis

| Comando | Descrição |
|---|---|
| `npm run dev` | Servidor de desenvolvimento (Vite) |
| `npm run build` | Build de produção |
| `npm run preview` | Preview do build de produção |
| `npm run lint` | Executa oxlint + eslint com auto-fix |
| `npm run format` | Formata os arquivos de `src/` com Prettier |

## Arquitetura

```
src/
├── components/
│   ├── MapContainer.vue   # instância do Leaflet; reage ao store
│   ├── AppSidebar.vue     # painel lateral com controles de camadas
│   └── LayerCard.vue      # card por camada (visibilidade, opacidade, legenda)
├── stores/
│   └── mapStore.js        # Pinia — fonte única de verdade do estado das camadas
├── config/
│   └── layers.js          # definição das camadas base e overlays por categoria
├── views/
│   └── HomeView.vue       # layout principal
└── assets/
    └── styles.json        # estilos de legenda gerados por data/styles.py
```

**Fluxo de dados das camadas:**

1. `mapStore.js` mantém o estado reativo: qual camada base está ativa e a visibilidade/opacidade de cada overlay.
2. `AppSidebar.vue` / `LayerCard.vue` leem e mutam o store diretamente.
3. `MapContainer.vue` observa o store com watchers e aplica as mudanças ao mapa via Leaflet — nunca guarda estado de camada próprio.

> **Restrição importante:** Leaflet não funciona em SSR. O mapa é inicializado em `onMounted` e destruído em `onUnmounted`. Não acesse `L` nem a instância do mapa fora desses hooks.

---

## Pipeline de dados (GeoPackage → Vector Tiles)

Esta seção documenta como os dados brutos em `data/dados_insa.gpkg` são convertidos em vector tiles servidos pela aplicação.

> ⚠️ **ATENÇÃO — leia antes de qualquer alteração**
>
> Sempre que uma camada for adicionada, removida ou alterada no GeoPackage, **todos os passos abaixo devem ser refeitos do zero**, incluindo a exclusão completa do diretório `public/tiles/insa_layers/` antes de reextrair.
>
> **Não existe atualização parcial.** Cada arquivo `.pbf` em `public/tiles/` contém *todas* as camadas embutidas naquele tile — não é possível apenas "adicionar os tiles da nova camada" sem sobrescrever tudo. Se o diretório antigo não for apagado, tiles obsoletos permanecem e podem causar comportamento inesperado.

### Por que regenerar tudo?

Os tiles em `public/tiles/insa_layers/{z}/{x}/{y}.pbf` **não são arquivos por camada** — cada arquivo `.pbf` contém *todas* as camadas embutidas naquele tile. Isso é gerado pelo Tippecanoe, que empacota múltiplos GeoJSONs em um único `.mbtiles`. Por isso, **não é possível adicionar só os tiles de uma nova camada** sem regenerar o arquivo inteiro. O processo completo precisa ser repetido a cada mudança.

### Ferramentas necessárias

Instale antes de começar:

```bash
# macOS
brew install gdal tippecanoe python3

# Verifica as versões
ogr2ogr --version   # GDAL 3.x
tippecanoe --version  # tippecanoe v2.x
python3 --version   # Python 3.x
```

### Diretório de trabalho

Todos os comandos a seguir devem ser executados **dentro de `data/`**:

```bash
cd data/
```

### Passo 1 — Exportar camadas do GeoPackage para GeoJSON

Use `ogr2ogr` para exportar **cada camada de interesse** para um arquivo GeoJSON reprojetado em WGS-84 (EPSG:4326). Um arquivo por camada:

```bash
ogr2ogr -f GeoJSON geojson/<nome_da_camada>.geojson \
  dados_insa.gpkg <nome_da_camada> \
  -t_srs EPSG:4326
```

Para listar todas as camadas disponíveis no GeoPackage:

```bash
ogrinfo -q dados_insa.gpkg
```

> **Nota:** o arquivo `geojson/layer_styles.geojson` é gerado automaticamente ao exportar a tabela interna de estilos do QGIS. Ele deve ser incluído no comando do Tippecanoe (passo 2), mas não precisa ser cadastrado como camada na aplicação.

### Passo 2 — Gerar o `.mbtiles` com Tippecanoe

Este passo empacota **todos** os GeoJSONs em um único arquivo de vector tiles. O comando abaixo é o definitivo do projeto — atualize-o sempre que adicionar ou remover uma camada:

```bash
tippecanoe \
  -o mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  geojson/declividade_sab_pb.geojson \
  geojson/declividade_sab_pb_original.geojson \
  geojson/declividade_sab_pb_pesos.geojson \
  geojson/eto_sab_pb_original.geojson \
  geojson/eto_sab_pb_pesos.geojson \
  geojson/geologia_sab_pb_original.geojson \
  geojson/geologia_sab_pb_pesos.geojson \
  geojson/ia_sab_pb_original.geojson \
  geojson/ia_sab_pb_pesos.geojson \
  geojson/iqc_sab_pb.geojson \
  geojson/iqs_sab_pb.geojson \
  geojson/layer_styles.geojson \
  geojson/municipios_pb_semiarido.geojson \
  geojson/precipitacao_sab_pb_original.geojson \
  geojson/precipitacao_sab_pb_pesos.geojson \
  geojson/solos_tipos_sab_pb_original.geojson \
  geojson/solos_tipos_sab_pb_pesos.geojson \
  geojson/textura_sab_pb_original.geojson \
  geojson/textura_sab_pb_pesos.geojson
```

Flags usadas:

| Flag | Motivo |
|---|---|
| `-z14 -Z2` | Gera tiles do zoom 2 (visão geral) ao 14 (detalhe) |
| `--no-feature-limit` | Não descarta feições por limite de quantidade por tile |
| `--no-tile-size-limit` | Não descarta feições por limite de tamanho do tile |
| `--extend-zooms-if-still-dropping` | Aumenta zoom máximo se ainda estiver descartando dados |
| `--no-tile-compression` | Salva os `.pbf` sem compressão (necessário para leitura direta pelo browser) |
| `--force` | Sobrescreve o `.mbtiles` existente sem perguntar |

> **Atenção:** o Tippecanoe pode demorar alguns minutos dependendo do volume de dados. O arquivo gerado (`insa_layers.mbtiles`) tem em torno de 90 MB — não comitar no git.

### Passo 3 — Apagar tiles antigos e reextrair

> ⚠️ **O `rm -rf` é obrigatório** — nunca pule este passo. Os tiles antigos não são sobrescritos, apenas somados. Se uma camada for removida do `.mbtiles`, os tiles dela permaneceriam em disco e seriam servidos pelo browser mesmo depois da atualização.

```bash
# Apaga TODOS os tiles antigos
rm -rf ../public/tiles/insa_layers

# Reextrai do .mbtiles recém-gerado
python3 export.py
```

O script lê `mbtiles/insa_layers.mbtiles` e grava cada tile em `../public/tiles/insa_layers/{z}/{x}/{y}.pbf`, aplicando a inversão de eixo Y necessária para compatibilidade com o padrão XYZ do Leaflet.

### Passo 4 — Extrair estilos do GeoPackage

```bash
python3 styles.py
```

Lê a tabela `layer_styles` do GeoPackage (criada pelo QGIS ao salvar estilos), extrai as cores de preenchimento por categoria e grava em `../src/assets/styles.json`. Esse arquivo é consumido pelo componente `LayerCard.vue` para montar a legenda e por `mapRenderer.js` para colorir as feições no canvas.

#### Quando `styles.py` não captura uma camada

O script só extrai cores de **preenchimento** (`fill`). Se uma camada no QGIS for estilizada apenas com **borda** (stroke), sem preenchimento, ela não aparecerá no `styles.json` gerado. Nesse caso, adicione a entrada manualmente:

```json
"nome_da_camada": {
  "Rótulo legenda": "stroke:#rrggbb"
}
```

O prefixo `stroke:` instrui o renderer a desenhar apenas o contorno do polígono, sem preenchimento. Exemplo real do projeto:

```json
"municipios_pb_semiarido": {
  "Limite municipal": "stroke:#ffffff"
}
```

---

## Como adicionar uma nova camada

Siga a checklist abaixo na ordem:

### 1. Dados

- [ ] Adicione a camada ao `dados_insa.gpkg` no QGIS e salve o estilo
- [ ] Exporte para GeoJSON: `ogr2ogr -f GeoJSON geojson/<camada>.geojson dados_insa.gpkg <camada> -t_srs EPSG:4326`
- [ ] Adicione o novo `.geojson` ao comando do Tippecanoe no Passo 2 acima (e atualize este README)
- [ ] Regere o `.mbtiles` (Passo 2)
- [ ] Regere os tiles (Passo 3: `rm -rf` + `python3 export.py`)
- [ ] Regere os estilos (Passo 4: `python3 styles.py`)
- [ ] Se a camada for stroke-only, adicione a entrada manualmente em `src/assets/styles.json`

### 2. Código

Abra `src/config/layers.js` e adicione um objeto na categoria adequada (ou crie uma nova):

```js
nova_camada: {
  label: 'Rótulo no menu',
  meta: 'Descrição curta',
  url: VECTOR_TILES_URL,
  sourceLayer: 'nome_exato_no_gpkg',   // deve bater com o nome da camada no Tippecanoe
  zIndex: 31,                           // maior = fica acima de outras camadas
  active: false,                        // false = camada começa oculta
  searchFields: ['campo1', 'campo2'],   // campos disponíveis no popup de clique
},
```

> `sourceLayer` deve ser **idêntico** ao nome da camada no GeoPackage (e ao nome usado no GeoJSON exportado). O Tippecanoe usa o nome do arquivo sem a extensão como `layer_id` dentro do `.pbf`.

### 3. Renderer (se necessário)

Se a nova camada tiver campos não listados em `src/utils/mapRenderer.js` → `possibleValues`, adicione-os para que o renderer consiga associar o valor da feição à cor correta da legenda:

```js
featureProps?.nome_do_campo_novo,
```

---

## Estrutura de `data/`

```
data/
├── dados_insa.gpkg          # fonte primária — GeoPackage com todas as camadas e estilos
├── geojson/                 # camadas exportadas em GeoJSON (intermediário)
│   ├── <camada>.geojson
│   └── ...
├── mbtiles/
│   └── insa_layers.mbtiles  # vector tiles empacotados (~90 MB, não versionar)
├── export.py                # extrai tiles do .mbtiles para public/tiles/
└── styles.py                # extrai estilos do .gpkg para src/assets/styles.json
```

> **`.mbtiles` e `geojson/` não devem ser versionados no git** por causa do tamanho. Certifique-se de que estão no `.gitignore`.

---

## Stack

| Lib | Uso |
|---|---|
| Vue 3 (Composition API + `<script setup>`) | Framework UI |
| Pinia | Gerenciamento de estado |
| Leaflet 1.x | Renderização do mapa |
| Bootstrap 5 | Layout e componentes visuais |
| FontAwesome 7 | Ícones (tree-shaken via `src/main.js`) |
| Oxlint + ESLint + Prettier | Qualidade de código |

## IDE recomendada

[VS Code](https://code.visualstudio.com/) com a extensão [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (desative o Vetur se estiver instalado).
