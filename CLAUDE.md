# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.
Read it fully at the start of every session before making any changes.

---

## Project overview

**DesertPB** is a WebGIS application developed by INSA (Instituto Nacional do
Semiárido) displaying thematic vector layers over the Paraíba semi-arid region
(Semiárido da PB). Built with Vue 3 + Vite. Serves vector tiles locally from
`public/tiles/` — there is no external map server dependency at runtime.

---

## Commands

```bash
npm run dev          # Development server with hot-reload (Vite)
npm run build        # Production build → dist/
npm run preview      # Preview production build
npm run lint         # oxlint + eslint with auto-fix (sequential)
npm run format       # Prettier format on src/
npm run deploy:tiles # Pack and deploy tiles to production server (see scripts/deploy-tiles.sh)
```

No test suite is configured.

---

## Stack

| Layer | Library |
|---|---|
| UI framework | Vue 3 — Composition API, `<script setup>` — JavaScript, NOT TypeScript |
| State | Pinia (`src/stores/mapStore.js`) |
| Map | Leaflet 1.x |
| Vector tiles | Custom `L.GridLayer` (`MapContainer.vue`) — fetches `.pbf` per tile, decodes with `vector-tile` + `pbf`, paints to a `<canvas>` via `mapRenderer.js`. NOT `leaflet.vectorgrid` — that package isn't a dependency. |
| Layout / UI | Bootstrap 5 |
| Icons | Bootstrap Icons 1.x — loaded via CDN in `index.html` (no npm package) |
| Theming | `src/composables/useTheme.js` — dark/light toggle; `data-theme` attribute on `<html>`; persisted in `localStorage` key `insa-theme`; `--accent` é o verde da marca DesertPB (`#22814a` claro / `#30a661` escuro) |
| Leaflet controls | Fullscreen, Locate, Medição e Escala implementados **nativamente** dentro do `ZoomHomeControl` em `MapContainer.vue` — sem plugins de terceiros. |
| Charts | Chart.js 4.x — importado modularmente em `LayerChartModal.vue`/`DashboardChart.vue`/`DashboardPieChart.vue` (não registrar globalmente) |
| Routing | vue-router 4.x — `createWebHashHistory` (GitHub Pages não tem rewrite de servidor para SPA) |
| Linting | Oxlint + ESLint + Prettier |

---

## Marca (logo)

A silhueta usada na marca DesertPB (favicon, navbar, `InicioView.vue`) vem do
contorno real de `limite_semiarido_pb` (o mesmo dado que renderiza no mapa) —
não é um desenho livre, para nunca reintroduzir a distorção que o arquivo de
logo original tinha.

A marca é uma grade de "pixels" (pequenos retângulos, com um espaçamento fino
entre eles) recortada pelo contorno real do semiárido, com um contorno sutil
(`stroke` preto, baixa opacidade) acompanhando a silhueta por cima. Cada pixel
é colorido com uma das 4 cores reais da escala do Índice de Vulnerabilidade à
Desertificação (IVD, ver `styles.json` → `ivd_sab`) — `#a6d96a` (Baixa),
`#e8ffc0` (Moderada), `#fdae61` (Alta), `#d7191c` (Muito Alta) — escolhida
pelo valor **médio real do IVD** (`ivd_sab`) amostrado naquele ponto do
território, não aleatoriamente: a marca é uma miniatura fiel do heatmap real
de vulnerabilidade do estado, não uma textura decorativa.

- `src/assets/logo-mark-fine.svg` — grade de 40 colunas (~550 pixels
  visíveis após o recorte pelo polígono), a versão de mais detalhe. Gerada,
  mas **não referenciada diretamente em nenhuma view hoje** — foi superada
  pelo `logo-lockup-fine.svg` no hero da `InicioView.vue`; mantida como a
  variante "só ícone, alta densidade" caso apareça um uso futuro que não
  queira o wordmark (og:image, ícone de PWA etc.).
- `src/assets/logo-mark-coarse.svg` — grade de 15 colunas (~85 pixels), para
  usos pequenos (navbar `AppNavbar.vue`, ~26px, só o ícone — ver abaixo) onde
  a grade fina vira ruído.
- `public/favicon.svg` — a versão coarse centralizada num viewBox quadrado
  (400×400) para o ícone da aba do navegador; `index.html` referencia esse SVG
  como ícone principal (`rel="icon"`).
- `public/favicon.ico` — renderizado a partir do `favicon.svg` (via `cairosvg`
  + `Pillow`, 6 resoluções: 16/32/48/64/128/256px), referenciado em
  `index.html` como `rel="alternate icon"` (fallback para navegadores sem
  suporte a favicon SVG). **Sempre gerado a partir do SVG atual** — nunca
  deixar o `.ico` ficar de uma versão antiga da marca; o silhueta bilobada do
  semiárido fica com aparência "borrada" em 16–32px independente do estilo
  (mosaico triangular ou grade de pixels), isso é uma limitação da forma em
  ícones pequenos, não um bug do gerador.
- `src/assets/logo-lockup-fine.svg` — o ícone fine (mesma grade de
  `logo-mark-fine.svg`) com o wordmark "DESERTPB" embutido no próprio SVG
  (não é texto HTML ao lado do ícone), empilhado bem colado na base da
  silhueta (6 unidades de espaço). É **a versão "completa" da marca hoje** —
  usada nos dois lugares onde o nome precisa aparecer junto ao ícone como uma
  peça só:
  - hero da `InicioView.vue` (`hero-mark`, 300px). Não existe mais um
    `<h1>DesertPB</h1>` de texto separado abaixo — o `<img>` em si é quem
    fica dentro do `<h1>` (`.hero-mark-heading`, com `alt="DesertPB"`), pra
    manter só um heading real na página sem duplicar o nome visualmente.
  - cabeçalho da `SobreView.vue` (`sobre-mark`, ~190px).
  - **Não usado no navbar** (`AppNavbar.vue`) — lá é só o ícone
    (`logo-mark-coarse.svg`, sem nome nenhum ao lado); o link já tem
    `aria-label="DesertPB — Início"` pra não perder o nome acessível.
- `src/assets/logo-lockup-coarse.svg` — mesma ideia, mas sobre a grade
  coarse. Gerada, mas **não referenciada em nenhuma view hoje** (a
  `SobreView.vue` também passou a usar a fine, que tem mais detalhe e fica
  bem mesmo em ~190px); mantida no gerador como opção pra um contexto futuro
  bem pequeno que precise do lockup completo (ex. um card estreito).
  - As letras são uma fonte de pixel própria (grade 5×7 por glifo, só
    maiúsculas, ver `WORDMARK_GLYPHS` em `generate_logo.py`) — uma fonte lisa
    (`system-ui`) foi tentada primeiro e destoava do mosaico de blocos do
    ícone; a fonte de pixel usa a mesma linguagem visual.
  - Todas as letras são pretas (`#000000`, cor pedida explicitamente — uma
    versão anterior tinha "PB" em vermelho, descartada) com contorno branco
    grosso (`stroke-width: 1`, não um traço sutil) e uma sombra projetada em
    SVG (`<filter id="wordmark-shadow"><feDropShadow ...>`, aplicada só ao
    grupo do texto). Contorno + sombra é o que garante contraste contra
    qualquer fundo — nenhuma moldura/placa atrás do texto (foi tentado, ver
    "Jumbotron" abaixo, e descartado). O SVG é estático (`<img>`, sem acesso
    a `data-theme`), então essa combinação precisa funcionar sozinha nos dois
    temas sem poder trocar de cor.

**Não editar os `.svg`/`.ico` manualmente** — regenerar com
`python scripts/generate_logo.py` (lê `limite_semiarido_pb` e `ivd_sab` do
GeoPackage + as faixas de `styles.json`; precisa de `cairosvg` e `Pillow`
instalados) sempre que o contorno do semiárido ou os dados/faixas do IVD
mudarem.

`--accent` (`src/assets/main.css`) foi trocado do azul original (`#0066cc` /
`#2997ff`) para um verde derivado da mesma família de cor da marca (`#22814a`
claro / `#30a661` escuro) — **não** é nenhuma das 4 cores exatas do IVD acima,
de propósito: reusar uma cor de classe de vulnerabilidade como cor genérica de
botão/UI criaria confusão semântica (ex. um botão "Explorar" na cor de "Muito
Alta" pareceria um alerta). `--accent-secondary` continua espelhando
`--accent` (não tem uso próprio no código hoje).

---

## Jumbotron da tela inicial (`src/components/HeroCarousel.vue`)

Carrossel de 10 fotos reais do semiárido paraibano (caatinga, vista aérea de
drone, afloramentos de granito, cactos em flor, pôr do sol no Lajedo de Pai
Mateus) usado como **fundo** de `.hero` em `InicioView.vue` —
`position: absolute; inset: 0; z-index: 0`, atrás de `.hero-inner` (logo,
eyebrow e texto, `z-index: 1`), não como uma seção separada abaixo do hero.
Por isso o texto do hero usa cores claras fixas (branco/quase-branco +
`text-shadow`) em vez de `var(--text-main)` — sobre uma foto, a cor de texto
do tema claro ficaria ilegível; o scrim escuro do carrossel
(`.carousel-scrim`) garante contraste nos dois temas.

O slide ativo (`.carousel-slide.is-active`) usa `z-index: 1` pra ficar por
cima durante o crossfade — por isso `.carousel-track` precisa do seu próprio
`z-index: 0` (cria um contexto de empilhamento que contém esse `1`). Sem
isso, o slide ativo "vaza" para fora de `.carousel-track` e cobre as setas,
os dots e o crédito (que são irmãos de `.carousel-track`, não filhos) — já
aconteceu uma vez. Se adicionar mais `z-index` dentro de `.carousel-track`
no futuro, manter esse contexto de empilhamento no lugar.

Autoplay a cada `INTERVAL_MS` (4200ms). Crossfade de 1.3s em
`var(--transition-curve)` (a mesma curva de easing do resto do app, não uma
curva improvisada só pro carrossel) + Ken Burns **alternado**: fotos em
posição ímpar (`:nth-of-type(odd)`) dão um leve zoom-in, as pares um leve
zoom-out com pan sutil na direção oposta — evita o efeito repetitivo de "zoom
pra dentro" igual em toda foto. A foto que está entrando também ganha um
leve efeito de foco (`filter: blur(6px)` → `blur(0)`, mesma duração do
crossfade), como um "puxão de foco" de câmera. Pausa em hover/foco e quando a
aba fica em segundo plano (`visibilitychange`), respeita
`prefers-reduced-motion` (desativa autoplay, zoom, pan e blur — ver o bloco
`@media (prefers-reduced-motion: reduce)`, que precisa repetir os mesmos
seletores `:nth-of-type` com a mesma especificidade pra realmente cancelar o
transform, não só zerar a versão "genérica"). Sem legenda de local por
decisão de produto — só o crédito do fotógrafo, obrigatório pela licença.

O wordmark pixelizado embutido no `logo-lockup-fine.svg` também precisa de
contraste contra a foto — depois de três tentativas com uma forma *visível*
atrás do texto (pílula com `backdrop-filter: blur()`, pílula com fundo
sólido, moldura arredondada com gradiente + borda), todas descartadas por não
ficarem boas visualmente, o contraste do texto em si vem de dentro do próprio
SVG (contorno branco grosso + sombra projetada em cada letra, ver seção
"Marca" acima) — **sem** nenhuma forma com borda/edge atrás dele.

- Imagens em `public/images/semiarido/*.jpg` — a maioria do Wikimedia Commons
  (CC BY / CC BY-SA, **exige atribuição**), mais 4 do Pixabay (licença
  Pixabay, atribuição opcional mas mantida por transparência) e uma do ISPN
  (Instituto Sociedade, População e Natureza). Cada slide carrega seu crédito
  em `slides` no `<script setup>` do componente e o exibe sobreposto na foto
  (canto inferior esquerdo) — **não remover o crédito** ao editar o
  componente, é obrigação da licença nas fotos do Commons, e boa prática nas
  demais.
- Para trocar/adicionar uma foto: baixar do Commons (checar a licença é
  reutilizável), redimensionar para no máximo ~2000px de largura mantendo
  proporção (`Pillow`, JPEG qualidade ~80, progressive), salvar em
  `public/images/semiarido/` e adicionar a entrada em `slides` (`src` via
  `` `${import.meta.env.BASE_URL}images/semiarido/<arquivo>.jpg` `` — nunca um
  caminho absoluto `/images/...` fixo, o app é publicado sob `/insa-front/`
  no GitHub Pages).

---

## Architecture

### Data flow

```
src/config/layers.js               ← SINGLE SOURCE OF TRUTH for layer definitions (OVERLAY_TREE)
        ↓
src/stores/mapStore.js             ← Pinia: reactive state (active base layer, overlay visibility/opacity)
        ↓
src/components/AppSidebar.vue      ← reads + mutates store; renders top-level tree nodes
src/components/SidebarTreeGroup.vue ← recursive: renders one group node, recurses into children
src/components/LayerCard.vue       ← per-layer card (toggle, opacity slider, legend) — leaf nodes only
        ↓
src/components/MapContainer.vue    ← owns Leaflet instance; watches store; applies changes to map
```

The sidebar renders `OVERLAY_TREE` as an actual nested tree (not a flat 2-level
accordion): `SidebarTreeGroup.vue` recursively renders itself for group nodes at
any depth, using `LayerCard.vue` unmodified for leaf nodes. See
"Layer configuration reference" below for the node shape.

Other components (not part of the layer flow):

- `GeoSearch.vue` — geocoding / coordinate search (address, DD, DMS); pans the map via the store
- `CoordDisplay.vue` — real-time cursor coordinates overlay (DD and DMS)

`src/views/DashboardView.vue` (and its subcomponents `DashboardMiniMap.vue`,
`DashboardPieChart.vue`, `DashboardChart.vue`, `DashboardTable.vue`) form an
**independent flow**, unrelated to `OVERLAY_TREE`/`mapStore.js`: they consume
`src/assets/dashboard_stats.json` (crossed with municípios) and `src/assets/stats.json`
(single-layer class breakdown, no crossing) directly, and are reached via
`src/router/index.js`, not through the sidebar.
`DashboardMiniMap.vue` keeps its **own** Leaflet map instance, separate from
`MapContainer.vue`'s, using `src/utils/createDashboardMvtLayer.js` for the índice
tile layer — a deliberate, simplified duplicate of the MVT tile-rendering logic
(see "Routing & navegação" below). The município boundary layer on the mini-map
is **not** MVT tiles — it's `public/data/municipios_pb_semiarido.geojson` loaded
via `L.geoJSON()`, so individual município polygons can be looked up by
`cod_ibge_m` and restyled (selection highlight, `fitBounds`) — something tile-based
rendering can't do, since a canvas tile has no addressable per-feature DOM/layer.

### Key design constraints — NEVER violate these

1. **Leaflet is client-only.** Initialize the map in `onMounted`, destroy in `onUnmounted`.
   Never access `L` or the map instance outside these lifecycle hooks.

2. **`MapContainer.vue` owns no layer state.** It reads the store via watchers and
   applies changes to Leaflet. It never stores which layers are active internally.

3. **`src/config/layers.js` is the only place to define layers.**
   No layer configuration exists anywhere else in the application. Do not add
   layer logic to the store or the map component.

4. **`OVERLAY_LAYERS` is derived automatically** from `OVERLAY_TREE` (recursive walk)
   inside `layers.js`. Never edit `OVERLAY_LAYERS` directly.

5. **`sourceLayer` must exactly match the layer name in the GeoPackage** (and the
   GeoJSON filename without extension used by Tippecanoe). Any divergence causes
   tiles to silently not render.

6. **Never add a per-layer `bounds` option to the `CustomMVTLayer` (`L.GridLayer`)
   in `MapContainer.vue`.** It was set to the tight `paraibaBounds` box until this
   bug: any layer whose real-world extent exceeds that box (e.g. `estados_ne`,
   which spans the whole Northeast) had every tile outside the box silently never
   fetched, rendering as disconnected line fragments. The map's own
   `map.setMaxBounds()` (with padding) already constrains panning — that's enough.

---

## Routing & navegação

The app has four routes, defined in `src/router/index.js`:

| Path | Component | Purpose |
|---|---|---|
| `/` | `src/views/InicioView.vue` | Landing page — DesertPB hero, IVD color-scale signature, feature highlights |
| `/mapa` | `src/views/HomeView.vue` | Map (sidebar + `MapContainer`) — the original single-screen app |
| `/dashboard` | `src/views/DashboardView.vue` | Município comparison dashboard |
| `/sobre` | `src/views/SobreView.vue` | About page — project/institutional text + development team, always last in the nav |

All four are lazy-loaded (`component: () => import(...)`) for automatic code-splitting.
`createWebHashHistory` is required, not `createWebHistory` — the production build
is published to GitHub Pages (`.github/workflows/deploy.yml`), which has no
server-side rewrite for SPA routing; a direct reload on `/dashboard` would 404
under history mode.

`src/App.vue` renders `AppNavbar.vue` (fixed header, `<RouterLink>` to all four
routes) above `<RouterView />`, instead of rendering `HomeView` directly. The
theme toggle lives in `AppNavbar.vue` (moved out of `AppSidebar.vue`) so it's
available on every screen — `useTheme()` is a module-level singleton, so moving
the button doesn't duplicate state.

`AppSidebar.vue` has **no brand header of its own** — its old `<header class="sidebar-header">`
(brand + collapse toggle) was removed because the brand duplicated `AppNavbar.vue`.
The sidebar-collapse toggle, however, lives back inside `AppSidebar.vue` — a
dedicated `.sidebar-collapse-row` pinned above `.sidebar-content` (outside the
scrollable area, so it never scrolls out of view), directly above the "Camadas
Base" section. It reuses `useSidebar()` (a module-level singleton) and is the
first focusable/visible element in the collapsed icon-only rail — same
collapse-aware icon-only styling as `.category-header`. It is **not**
conditionally rendered per-route (it lived in `AppNavbar.vue` gated on
`route.path` before; now that it's inside `AppSidebar.vue` itself, it's simply
absent whenever `AppSidebar.vue` isn't mounted, i.e. outside `/mapa`).

**Layout consequence:** introducing a fixed-height navbar above everything means
`AppSidebar.vue`'s `#sidebar` can no longer be `height: 100vh` (it would overflow
its now-shorter container and clip `GeoSearch.vue` at the bottom) — it must be
`height: 100%`, relying on the `html/body/#app { height: 100% }` chain already in
`main.css`. If you add more views, keep following this pattern rather than
reintroducing a `100vh` rule anywhere below the navbar.

---

## Layer configuration reference (`src/config/layers.js`)

This is the **only file to edit** when adding, removing, or changing a layer.

### Structure — `OVERLAY_TREE` (recursive)

```js
export const BASE_LAYERS = { /* OSM, Satellite, etc. — radio-button selection */ }

export const OVERLAY_TREE = [
  {
    key:      'group_key',           // unique across the whole tree
    label:    'Label shown in accordion',
    icon:     'bi-icon-name',        // Bootstrap Icons class
    layer:    null,                  // null = pure group node (no toggle of its own)
    children: [ /* more nodes, same shape, recursively */ ],
  },
  {
    key:   'layer_key',
    layer: { /* see "Layer object fields" below */ },
    // no `children` = leaf node, rendered as a LayerCard
  },
]

// OVERLAY_LAYERS is auto-generated by recursively walking OVERLAY_TREE — do not edit directly
```

A node is one of two things — never both:
- **Group node** (`layer: null`, has `children`) — renders as an accordion header
  (`SidebarTreeGroup.vue`), any depth. Used for pure taxonomy levels like
  "Índices de Vulnerabilidade" or "Escores de Vulnerabilidade" that aren't themselves a map layer.
- **Leaf node** (`layer: {...}`, no `children`) — renders as a `LayerCard`.

If something is **both** a toggleable layer and a parent of other layers (e.g. IVS
is a composite index *and* has "Escores de Vulnerabilidade" beneath it), model it as a
group whose **first child** is the leaf for that composite layer — do not put
`layer` and `children` on the same node. This keeps `LayerCard.vue` free of any
"is this also a group" branching.

**Order matters and is fixed** — the sidebar renders `children` arrays in
declaration order, with no runtime re-sorting. The order in `layers.js` must
match the intended hierarchy exactly.

### Layer object fields

```js
layer: {
  // ── Required ──────────────────────────────────────────────────────────────
  label:        'Human-readable name shown in sidebar and popup',
  meta:         'Short description shown below the label',
  url:          VECTOR_TILES_URL,          // do not change — points to public/tiles/
  sourceLayer:  'exact_name_in_gpkg',      // must match GeoPackage layer name exactly
  zIndex:       20,                        // higher = rendered on top
  active:       false,                     // true = visible on page load

  // ── Search bar ────────────────────────────────────────────────────────────
  searchFields: ['field1', 'field2'],      // fields inspected by the search bar
  fieldTypes:   { field1: 'string',
                  field2: 'number' },      // 'string' (substring) or 'number' (operators)

  // ── Click popup ───────────────────────────────────────────────────────────
  popUpFields:  ['field1', 'field2'],      // fields shown in popup, in this order
                                           // if omitted: shows all fields except id/gid/fid
  descFields:   { field1: 'Friendly label',
                  field2: 'Another label' }, // human-readable label per field
  noPopup:      true,                      // omit or false = normal popup behavior;
                                           // true = layer is excluded entirely from
                                           // click-popup queries (e.g. pure boundary
                                           // layers with nothing meaningful to show)
}
```

> **`descFields` convention:** every entry must be a human-readable Portuguese label —
> never use the technical field name as its own value (e.g., `{ IVS: 'IVS' }` is wrong;
> `{ IVS: 'Índice de Vulnerabilidade do Solo' }` is correct).
> These labels surface in two places: the popup left column and the search panel header
> (`"Buscar por <label>"`), so they must be meaningful to end users.

```js
```

### `zIndex` conventions

| Range | Use |
|---|---|
| 1 | Base tile layers |
| 10–28 | Composite vulnerability indices (IVD, IVS, IVV, IVC, IVM) and their "Escores de Vulnerabilidade" components, ordered by category |
| 30+ | Administrative boundaries (always on top) |

---

## Existing layers (current state)

All layers cover the **Paraíba semi-arid region (Semiárido da PB)**, except
`limite_do_semiarido_br`, which outlines the wider Brazilian semi-arid region. They
come from the delivered branch of the information tree — IVD → Índices de
Vulnerabilidade → IVS/IVV/IVC/IVM → Escores de Vulnerabilidade. The "Indicadores de
Vulnerabilidade" branch (raw Pedologia/Geomorfologia/Litologia/Vegetação/Climáticos/Manejo
data) has not been delivered yet and has no layers in the app.

> These categories were previously named "Índices/Escores de Qualidade" (IQS/IQV/IQC/IQM).
> The GeoPackage delivery renamed both the taxonomy and every `sourceLayer`/field to
> "Vulnerabilidade" (IVS/IVV/IVC/IVM) — the underlying classification (values, ranges,
> colors) is unchanged, only the naming.

Every score field (`ivs`, `ivv`, `ivc`, `ivm`, `ivd`, and all `*escores*`
fields below) is a **continuous numeric index**, not discrete classes — matched via
the numeric-range mode in `mapRenderer.js`/`stats.py`.

| `sourceLayer` | Category | Description |
|---|---|---|
| `limite_semiarido_pb` | Limites | Semiárido PB region outline (stroke-only, no popup, no chart) |
| `municipios_pb_semiarido` | Limites | Municipal boundaries (stroke-only) |
| `estados_ne` | Limites | Northeast state boundaries (stroke-only, no popup, no chart) |
| `limite_do_semiarido_br` | Limites | Brazilian semi-arid region outline (stroke-only, no popup, no chart) |
| `ivd_sab` | IVD | Índice de Vulnerabilidade à Desertificação (composite) |
| `ivs` | IVS | Índice de Vulnerabilidade do Solo (composite) |
| `declividade_escores_de_vulnerabilidade` | IVS | Slope — vulnerability score |
| `geologia_escores_de_vulnerabilidade` | IVS | Geology — vulnerability score |
| `textura_escores_de_vulnerabilidade` | IVS | Soil texture — description + vulnerability score |
| `tipos_de_solos_escores_de_vulnerabilidade` | IVS | Soil types — description + vulnerability score |
| `ivv` | IVV | Índice de Vulnerabilidade da Vegetação (composite) |
| `ndvi_escore_de_vulnerabilidade` | IVV | NDVI — vulnerability score |
| `carbono_organico_escores_de_vulnerabilidade` | IVV | Soil organic carbon — vulnerability score |
| `suscetibilidade_erosao_escore_de_vulnerabilidade` | IVV | Water erosion susceptibility — vulnerability score |
| `ivc` | IVC | Índice de Vulnerabilidade Climática (composite) |
| `ia_escores_de_vulnerabilidade` | IVC | Aridity index — vulnerability score |
| `precipitacao_escores_de_vulnerabilidade` | IVC | Rainfall — vulnerability score |
| `eto_escores_de_vulnerabilidade` | IVC | Evapotranspiration — vulnerability score |
| `ivm` | IVM | Índice de Vulnerabilidade de Manejo (composite) |
| `pressao_animal_escores_de_vulnerabilidade` | IVM | Animal pressure — vulnerability score |
| `focos_queimadas_escores_de_vulnerabilidade` | IVM | Fire outbreaks — vulnerability score |
| `densidade_demografica_rural_escores_de_vulnerabilidade` | IVM | Rural demographic density — vulnerability score |
| `idhm_escores_de_vulnerabilidade` | IVM | Municipal HDI — vulnerability score |

**`municipios_pb_semiarido`, `limite_semiarido_pb`, `estados_ne` and `limite_do_semiarido_br`
are stroke-only** — their entries in `src/assets/styles.json` must use `"type": "stroke"`
(see the Styles section below for the full schema). All four also set `noPopup: true`
in `layers.js` (except `municipios_pb_semiarido`, which has a real popup) — they're pure
boundary outlines with no attributes worth surfacing in a popup, and being stroke-only
they're automatically skipped by `stats.py` so no chart button appears either.

---

## Data pipeline (GeoPackage → vector tiles)

> ⚠️ Every time a layer is added, removed, or changed in the GeoPackage,
> **all steps below must be re-run from scratch**. There is no partial update.
> Always delete `public/tiles/insa_layers/` before re-extracting.

Todos os comandos rodam a partir da **raiz do projeto**. Os scripts Python ficam
em `scripts/` e resolvem os paths automaticamente via `Path(__file__).parent.parent`.

### Step 1 — Export each layer from GeoPackage to GeoJSON

```bash
# List available layers
ogrinfo -q data/dados_insa.gpkg

# Export one layer (repeat for each)
ogr2ogr -f GeoJSON data/geojson/<layer_name>.geojson \
  data/dados_insa.gpkg <layer_name> \
  -t_srs EPSG:4326
```

### Step 2 — Generate `.mbtiles` with Tippecanoe

```bash
tippecanoe \
  -o data/mbtiles/insa_layers.mbtiles \
  -z14 -Z2 \
  --no-feature-limit \
  --no-tile-size-limit \
  --extend-zooms-if-still-dropping \
  --no-tile-compression \
  --force \
  data/geojson/municipios_pb_semiarido.geojson \
  data/geojson/limite_semiarido_pb.geojson \
  data/geojson/limite_do_semiarido_br.geojson \
  data/geojson/estados_ne.geojson \
  data/geojson/ivd_sab.geojson \
  data/geojson/ivs.geojson \
  data/geojson/ivv.geojson \
  data/geojson/ivc.geojson \
  data/geojson/ivm.geojson \
  data/geojson/declividade_escores_de_vulnerabilidade.geojson \
  data/geojson/geologia_escores_de_vulnerabilidade.geojson \
  data/geojson/textura_escores_de_vulnerabilidade.geojson \
  data/geojson/tipos_de_solos_escores_de_vulnerabilidade.geojson \
  data/geojson/ndvi_escore_de_vulnerabilidade.geojson \
  data/geojson/carbono_organico_escores_de_vulnerabilidade.geojson \
  data/geojson/suscetibilidade_erosao_escore_de_vulnerabilidade.geojson \
  data/geojson/ia_escores_de_vulnerabilidade.geojson \
  data/geojson/precipitacao_escores_de_vulnerabilidade.geojson \
  data/geojson/eto_escores_de_vulnerabilidade.geojson \
  data/geojson/pressao_animal_escores_de_vulnerabilidade.geojson \
  data/geojson/focos_queimadas_escores_de_vulnerabilidade.geojson \
  data/geojson/densidade_demografica_rural_escores_de_vulnerabilidade.geojson \
  data/geojson/idhm_escores_de_vulnerabilidade.geojson \
  data/geojson/layer_styles.geojson
```

> `layer_styles.geojson` is the QGIS style table — include it in the command but
> do not register it as an application layer.

> The `.mbtiles` file is ~138 MB — it is gitignored. Do not commit it.

### Step 3 — Delete old tiles and re-extract

```bash
rm -rf public/tiles/insa_layers      # MANDATORY — never skip this
python scripts/export.py             # writes public/tiles/insa_layers/{z}/{x}/{y}.pbf
```

### Step 4 — Extract styles

```bash
python scripts/styles.py    # writes src/assets/styles.json from layer_styles (QML) in the GeoPackage
```

`styles.py` parses the **QML** (QGIS's native XML style format, stored in the
`layer_styles.styleQML` column), not the SLD — QML preserves the renderer type
(categorized vs. graduated) and each class's human-authored label
(e.g. `"Alta"`, `"Moderada"`), which the SLD/regex approach used to discard.
Rows whose `f_table_name` isn't a real table in the GeoPackage are skipped
automatically (the GeoPackage can contain stray/duplicate style rows).

`singleSymbol`-styled layers (e.g. `municipios_pb_semiarido`, `limite_semiarido_pb`,
`estados_ne`, `limite_do_semiarido_br` — all rendered stroke-only) are **not**
captured automatically — add them manually.

> ⚠️ **`styles.py` overwrites `src/assets/styles.json` entirely.** Any manual entry
> will be lost after every pipeline run. Always restore manual entries immediately
> after running `styles.py`.
> Current manual entries that must be re-added:
>
> ```json
> "municipios_pb_semiarido": {
>   "type": "stroke",
>   "field": null,
>   "classes": [
>     { "label": "Limite municipal", "color": "#ffffff" }
>   ]
> },
> "limite_semiarido_pb": {
>   "type": "stroke",
>   "field": null,
>   "classes": [
>     { "label": "Limite do Semiárido PB", "color": "#ff2424" }
>   ]
> },
> "estados_ne": {
>   "type": "stroke",
>   "field": null,
>   "classes": [
>     { "label": "Limite estadual", "color": "#000000" }
>   ]
> },
> "limite_do_semiarido_br": {
>   "type": "stroke",
>   "field": null,
>   "classes": [
>     { "label": "Limite do Semiárido BR", "color": "#ffd700" }
>   ]
> }
> ```

### Step 5 — Generate area statistics

```bash
python scripts/stats.py    # writes src/assets/stats.json
```

Calcula a área (km², EPSG:5880) de cada classe para todas as camadas em
`styles.json`. Deve ser rodado sempre que `styles.json` for atualizado.

### Step 6 — Generate dashboard comparison stats

```bash
python scripts/dashboard_stats.py    # writes src/assets/dashboard_stats.json
```

Cruza (overlay geométrico) `municipios_pb_semiarido` com cada uma das 5 camadas
de índice composto (`ivs`, `ivv`, `ivc`, `ivm`, `ivd_sab`), produzindo valor médio
ponderado por área + classe dominante por município. Depende de `styles.json`
(Step 4) — re-executar sempre que o estilo de qualquer uma dessas 5 camadas mudar.
Veja "Dashboard de comparação" abaixo para o schema completo.

### Required tools (macOS)

```bash
brew install gdal tippecanoe python3
```

---

## Deploying tiles to production

After regenerating tiles locally (pipeline steps 2–3), publish to the server:

```bash
npm run deploy:tiles
```

**Script:** `scripts/deploy-tiles.sh`
**Server:** `ubuntu@2.25.137.181` (`sistema.sigrural.com.br`) — SSH key access, no password
**Remote path:** `/var/www/html/tiles/insa_layers/`

What the script does:
1. Packs `public/tiles/insa_layers/` → `insa_layers.tar.gz` (~42 MB) using `COPYFILE_DISABLE=1`
   to suppress macOS extended-attribute warnings on the Linux server
2. Sends via SCP to `/home/ubuntu/`
3. On the server: removes old tiles (`rm -rf insa_layers`), extracts, removes the archive
4. Cleans up the local `.tar.gz`

---

## Deploying the app (GitHub Pages)

`.github/workflows/deploy.yml` builds and deploys automatically on every push to
`main` (`npm run build` → `dist/` → GitHub Pages). No manual step needed beyond
`git push origin main`. The production build reads `.env.production`
(`VITE_TILES_URL=https://sistema.sigrural.com.br/tiles/...`), so **tiles must be
deployed to the tile server (`npm run deploy:tiles`) before or alongside pushing
app code** — otherwise the live site points at tiles that don't exist yet.

---

## Checklist: adding a new layer

### Data side

- [ ] Add layer to `dados_insa.gpkg` in QGIS and save the style
- [ ] Export to GeoJSON: `ogr2ogr -f GeoJSON data/geojson/<layer>.geojson data/dados_insa.gpkg <layer> -t_srs EPSG:4326`
- [ ] Add the new `.geojson` to the Tippecanoe command in Step 2 (and update this file)
- [ ] Re-run Step 2 (generate `.mbtiles`)
- [ ] Re-run Step 3 (`rm -rf public/tiles/insa_layers` + `python scripts/export.py`)
- [ ] Re-run Step 4 (`python scripts/styles.py`)
- [ ] Restore any manual entries in `src/assets/styles.json` (styles.py overwrites the file — see warning above)
- [ ] If stroke-only, add entry manually to `src/assets/styles.json`
- [ ] Re-run Step 5 (`python scripts/stats.py`) to update `src/assets/stats.json`
- [ ] If the changed layer is one of the 5 composite indices (`ivs`/`ivv`/`ivc`/`ivm`/`ivd_sab`),
      also re-run Step 6 (`python scripts/dashboard_stats.py`)

### Code side

- [ ] Add the layer object to the correct category in `src/config/layers.js`
- [ ] Set `sourceLayer` to exactly match the GeoPackage layer name

---

## Renderer (`src/utils/mapRenderer.js`)

Reads `src/assets/styles.json` and paints each feature on a canvas based on its
attribute values. `styles.json` already carries the field name to read
(`style.field`, extracted from the QML `attr` in Step 4) and the classification
type, so the renderer never needs a hardcoded list of field names — adding a
layer to `layers.js` with the right `sourceLayer` is enough.

`getThematicColor(sourceLayer, featureProps)` branches on `style.type`:
1. **`categorized`** — exact match: picks the class whose `value` is closest
   to `featureProps[style.field]` (QGIS "Categorized" symbology).
2. **`graduated`** — range match: first class whose `max` (upper bound) is
   `>= featureProps[style.field]` (QGIS "Graduated" symbology).
3. **`stroke` / `single`** — fixed color, no attribute lookup (e.g. municipal
   boundaries).

Getting `categorized` vs `graduated` wrong produces a legend that *looks*
plausible (colors still render) but shows synthesized numeric ranges instead
of the real QGIS class labels — always re-run Step 4 after any style change
in QGIS rather than hand-editing `styles.json`.

---

## Statistics (`src/assets/stats.json`)

Gerado por `scripts/stats.py`. Contém a área (km²) de cada classe para cada camada.
Usado pelo frontend para exibir estatísticas na legenda.

```json
{
  "layer_name": {
    "classes": [
      { "label": "Alta", "area_km2": 9020.0, "color": "#30b000" }
    ],
    "total_km2": 53875.3,
    "field_used": "ivc"
  },
  "municipios_pb_semiarido": null
}
```

`stats.py` reads `style.field`/`style.type`/`style.classes` from `styles.json`
directly (no column-guessing) and classifies each feature the same way the
frontend renderer does — `categorized` (exact value match) or `graduated`
(upper-bound range match) — so areas always line up with what's shown on the map.

Todas as classes definidas em `styles.json` aparecem no array `classes`, mesmo que
`area_km2` seja `0.0` (classe presente no estilo mas sem polígonos no recorte PB).
Isso garante que o gráfico do frontend exiba o mesmo número de barras que a legenda.

Regenerar sempre que `styles.json` for atualizado: `python scripts/stats.py`.

---

## Dashboard de comparação (`src/assets/dashboard_stats.json`)

Gerado por `scripts/dashboard_stats.py`. Cruza (overlay geométrico) cada uma das
5 camadas de índice composto com `municipios_pb_semiarido` — necessário porque
essas camadas são grids derivados de raster, sem campo de município próprio, então
não há chave de atributo comum para um join direto.

```json
{
  "indices_meta": {
    "ivs": { "sourceLayer": "ivs", "field_used": "ivs" },
    "ivc": { "sourceLayer": "ivc", "field_used": "ivc" }
  },
  "municipios": {
    "2500106": {
      "cod_ibge_m": "2500106",
      "nm_municip": "Água Branca",
      "slug": "agua-branca",
      "indices": {
        "ivs": { "value": 1.501, "class_label": "1,48 - 1,61 - Moderada", "class_color": "#fdae61" }
      }
    }
  }
}
```

- `indices_meta[key].field_used` — o campo real lido em cada camada (ex. `ivc` usa
  `ivc`, `ivd_sab` usa `ivd`). O frontend **nunca** hardcoda esses nomes —
  sempre resolve o label em português via `OVERLAY_LAYERS[key].descFields[field_used]`
  (`layers.js` continua a única fonte de nomes amigáveis).
- `value` — média do índice dentro do município, ponderada pela área de cada
  fragmento da interseção geométrica.
- `class_label`/`class_color` — classe dominante (maior área agregada) dentro do
  município, usando as mesmas classes de `styles.json`.
- `value`/`class_label`/`class_color`: `null` quando não há interseção geométrica
  suficiente entre o município e aquela camada de índice (raro — a maioria dos
  municípios tem pelo menos parte de seu território coberta).
- Regenerar sempre que `styles.json` for atualizado para uma das 5 camadas de
  índice composto: `python scripts/dashboard_stats.py`.

### Gráfico de pizza (`DashboardPieChart.vue`) — sem cruzamento

"Distribuição por classe" no dashboard **não** usa `dashboard_stats.json` — usa
`src/assets/stats.json` diretamente (a mesma fonte de `LayerChartModal.vue`),
porque é a distribuição de área por classe da camada de índice sozinha, sem
cruzar com municípios. Se um índice ganhar um valor em `stats.json`, o gráfico de
pizza do dashboard já reflete automaticamente — nenhum dado adicional a gerar.

### GeoJSON de municípios (`public/data/municipios_pb_semiarido.geojson`)

O mini-mapa do dashboard (`DashboardMiniMap.vue`) renderiza o contorno dos
municípios a partir deste GeoJSON estático via `L.geoJSON()` — **não** dos vector
tiles MVT (diferente de todas as outras camadas do projeto). Isso é intencional:
tiles MVT não dão acesso a uma feição individual endereçável no cliente (um tile
é só um canvas pintado), então não dá para destacar/dar `fitBounds` num único
município a partir de tiles. Um `L.GeoJSON` mantém uma `L.Layer` por feição,
indexável por `cod_ibge_m`, o que permite a reatividade tabela → mapa (seleciona
uma linha, o mini-mapa destaca a borda e dá zoom naquele município).

Gerado com:

```bash
ogr2ogr -f GeoJSON public/data/municipios_pb_semiarido.geojson \
  data/dados_insa.gpkg municipios_pb_semiarido \
  -t_srs EPSG:4326 -simplify 0.0015
```

`-simplify 0.0015` reduz o arquivo de ~1,9 MB para ~450 KB (precisão de sobra
para a escala de exibição do mini-mapa). Diferente de `data/geojson/` (gitignored,
regenerado a cada build do pipeline), este arquivo vive em `public/data/` e **é
versionado** — regenerar manualmente só se os limites municipais no GeoPackage
mudarem.

---

## Styles (`src/assets/styles.json`)

Auto-generated by `scripts/styles.py` from each layer's QML (`layer_styles.styleQML`
in the GeoPackage). Structure:

```json
{
  "layer_name": {
    "type": "categorized",
    "field": "etoescores",
    "classes": [
      { "value": 1, "label": "1- Muito Alta", "color": "#2b83ba" },
      { "value": 1.2, "label": "1,2 - Alta", "color": "#aaddd9" }
    ]
  },
  "other_layer": {
    "type": "graduated",
    "field": "ivc",
    "classes": [
      { "max": 1.216, "label": "1 - 1,22 - Alta", "color": "#2b83ba" },
      { "max": 1.48, "label": "1,22 - 1,48 -Moderada", "color": "#c7e8ad" }
    ]
  },
  "municipios_pb_semiarido": {
    "type": "stroke",
    "field": null,
    "classes": [{ "label": "Limite municipal", "color": "#ffffff" }]
  }
}
```

- `type: "categorized"` — QGIS "Categorized" symbology; classes match by exact `value`.
- `type: "graduated"` — QGIS "Graduated" symbology; classes match by `max` (upper bound of the range).
- `type: "stroke"` / `"single"` — fixed color, no attribute lookup; `"stroke"` renders outline-only.
- `label` is the **exact text authored in QGIS** (not reformatted) — it's what
  the sidebar legend and the stats chart both display, so getting the QGIS
  classification right is what makes the frontend right.
- `field` is the attribute QGIS classified on (`renderer-v2[@attr]` in the QML) —
  used by both the map renderer and `stats.py` to read the right property.

---

## Search bar behavior

- `searchFields`: fields inspected when the user types
- `fieldTypes`: determines comparison mode
  - `'string'` → case-insensitive substring match
  - `'number'` → supports operators `>`, `<`, `>=`, `<=`, `=`
- Fields absent from `fieldTypes` default to string matching

---

## What NOT to do

- Do not add layer definitions anywhere other than `src/config/layers.js`
- Do not access Leaflet (`L`) or the map instance outside `onMounted`/`onUnmounted`
- Do not store layer state inside `MapContainer.vue`
- Do not edit `OVERLAY_LAYERS` directly — it is derived from `OVERLAY_TREE`
- Do not put both `layer` and `children` on the same `OVERLAY_TREE` node — if a
  composite layer also has sub-items, make it a group whose first child is the leaf
- Do not commit `data/mbtiles/` or `data/geojson/` — both are gitignored due to size
- Do not run a partial pipeline update — always regenerate everything from scratch
- Do not assume `sourceLayer` is flexible — it must be byte-identical to the GeoPackage layer name
- Do not register Chart.js globally — always import only the needed modules in the component that uses it
- Do not forget to call `chartInstance?.destroy()` in `onUnmounted` when using Chart.js
- Do not add a `bounds` option to the overlay `CustomMVTLayer` in `MapContainer.vue`
  — it silently drops tiles outside that box for any layer with a wider extent
  than the Semiárido PB region (see Key design constraint #6)
- Do not hardcode field names (`ivs`/`ivc`/`ivd`/etc.) in `DashboardView.vue`
  — always read `field_used` from `dashboard_stats.json`
- Do not create a Pinia store for the dashboard unless the state needs to be
  shared outside `DashboardView.vue` — index selection, sort, and filter are
  local `ref`s today, and that's intentional
- Do not merge `src/utils/createDashboardMvtLayer.js` with the tile-rendering
  logic in `MapContainer.vue` — it's an intentional simplified duplicate (no
  search filter, no match counting, no `mapStore` dependency), not an oversight.
  `DashboardMiniMap.vue` is deliberately independent of the main map/store.
- Do not switch the município layer in `DashboardMiniMap.vue` back to MVT tiles
  — it's GeoJSON (`public/data/municipios_pb_semiarido.geojson`) on purpose, so
  individual municípios are addressable by `cod_ibge_m` for the table → map
  selection highlight. Tiles can't do per-feature lookup client-side.
- Do not regenerate `public/data/municipios_pb_semiarido.geojson` through the
  tile pipeline (Steps 1–3) — it's independent, versioned in git (unlike
  `data/geojson/`), and only needs regenerating if municipal boundaries change
  in the GeoPackage (see "GeoJSON de municípios" above for the command)

---

## Session startup ritual

At the beginning of each session, run:

```bash
git log --oneline -10
```

Then read this file and `src/config/layers.js` to understand the current state
before making any changes.