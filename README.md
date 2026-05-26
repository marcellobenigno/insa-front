# INSA Front

Aplicação web de mapeamento GIS desenvolvida com Vue 3 + Vite. Exibe camadas vetoriais do INSA sobre um mapa base interativo (OpenStreetMap ou ESRI Satellite), com suporte a vector tiles locais e legendas dinâmicas por camada.

## Pré-requisitos

- **Node.js** `^20.19.0` ou `>=22.12.0`
- **GeoServer** rodando em `http://localhost:8080/geoserver/insa/wms` (necessário para camadas WMS; as camadas base funcionam sem ele)

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
│   └── layers.js          # definição das camadas base e overlays
├── views/
│   └── HomeView.vue       # layout principal
└── assets/
    └── styles.json        # estilos de legenda gerados por styles.py
```

**Fluxo de dados das camadas:**

1. `mapStore.js` mantém o estado reativo: qual camada base está ativa e a visibilidade/opacidade de cada overlay.
2. `AppSidebar.vue` / `LayerCard.vue` leem e mutam o store diretamente.
3. `MapContainer.vue` observa o store com watchers e aplica as mudanças ao mapa via Leaflet — nunca guarda estado de camada próprio.

> **Restrição importante:** Leaflet não funciona em SSR. O mapa é inicializado em `onMounted` e destruído em `onUnmounted`. Não acesse `L` nem a instância do mapa fora desses hooks.

## Pipeline de dados

Os arquivos de dados ficam em `data/`. Execute os passos abaixo a partir desse diretório.

### 1 — Converter GeoPackage → GeoJSON

Exporta cada camada de `dados_insa.gpkg` para um arquivo GeoJSON reprojetado em WGS-84 (EPSG:4326):

```bash
for camada in $(ogrinfo -q dados_insa.gpkg | awk -F': ' '{print $2}'); do
    echo "Convertendo camada: $camada ..."
    ogr2ogr -f "GeoJSON" "geojson/${camada}.geojson" dados_insa.gpkg "$camada" -t_srs EPSG:4326
done
```

### 2 — Gerar vector tiles com tippecanoe

Empacota todos os GeoJSONs em um único arquivo `.mbtiles`:

```bash
tippecanoe -o mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  geojson/*.geojson
```

### 3 — Exportar tiles e estilos

```bash
python3 export.py   # extrai os tiles do .mbtiles para public/tiles/insa_layers/{z}/{x}/{y}.pbf
python3 styles.py   # lê os estilos de layer_styles no .gpkg e gera src/assets/styles.json
```

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
