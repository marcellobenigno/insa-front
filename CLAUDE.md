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
  `logo-mark-fine.svg`) com o wordmark "DesertPB" embutido no próprio SVG
  (não é texto HTML ao lado do ícone), empilhado logo abaixo da silhueta
  (`WORDMARK_VGAP` de espaço). É **a versão "completa" da marca hoje** — usada
  nos dois lugares onde o nome precisa aparecer junto ao ícone como uma peça
  só:
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
  - O wordmark "DesertPB" é **texto SVG de verdade** (`<text>`, ver
    `render_lockup_svg` em `generate_logo.py`), na mesma pilha de fontes do
    corpo do site (`WORDMARK_FONT_FAMILY` = a mesma lista de `body {
    font-family }` em `src/assets/base.css`) — não uma fonte de pixel própria
    imitando o mosaico do ícone (existiu uma versão assim antes; descartada a
    pedido do usuário, que queria correspondência visual com o resto do site
    em vez de uma estética "retrô" isolada). Usar a mesma lista de fallbacks
    (não só a fonte "ideal") importa: em quem visita fora do macOS/Safari,
    onde `-apple-system`/`BlinkMacSystemFont` não existem, a marca cai no
    mesmo fallback que o restante do texto do site cai para aquele
    visitante — ao contrário de converter o texto em contornos vetoriais
    fixos (o que congelaria pra sempre a fonte da máquina que rodou o
    gerador, e poderia destoar da fonte real exibida pelo navegador de quem
    acessa o site). `font-weight: 700`, o mesmo peso dos títulos mais
    proeminentes do site (ex. `.feature-card h2`).
  - `WORDMARK_CANVAS_W`/`WORDMARK_CANVAS_H` reservam uma área generosa pro
    texto — texto SVG não dá pra medir com exatidão em tempo de geração (a
    largura real varia por fonte/plataforma), e um `<img>` sempre recorta no
    `viewBox` (não respeita `overflow: visible` da própria tag `<svg>`), então
    a margem existe pra nunca cortar "DesertPB" em negrito em nenhuma fonte
    do fallback, calibrada visualmente comparando várias fontes candidatas.
  - "Desert" é preto (`#000000`, cor pedida explicitamente) e "PB" é vermelho
    (`#ff2424`, a pedido do usuário) — o mesmo vermelho do contorno de
    `limite_semiarido_pb` em `styles.json` ("Limite do Semiárido PB"): as
    letras "PB" (Paraíba) na mesma cor que desenha a fronteira da Paraíba no
    mapa, não um vermelho arbitrário. Implementado com um `<tspan fill=...>`
    só em "PB" dentro do mesmo `<text>`.
  - **Centralização (horizontal e vertical) é manual, não via
    `text-anchor="middle"`/`dominant-baseline`** — `measure_text_width` e
    `text_baseline_y` (`generate_logo.py`) medem o avanço horizontal e o
    `ascent`/`descent` do texto com `cairo.Context.text_extents`/
    `font_extents` (fonte de referência só pra medida,
    `WORDMARK_MEASURE_FONT = "Arial"`), e o `<text>` usa `text-anchor="start"`
    com `x`/`y` calculados a partir dessas medidas. Dois bugs cross-renderer
    motivaram isso, não só um: (1) `text-anchor="middle"` com um `<tspan>` de
    cor diferente no meio (sem `x`/`y` próprios) depende do renderizador
    calcular certo o "text chunk" combinado — o `cairosvg` usado pra
    pré-visualizar durante o desenvolvimento **não** calcula isso direito
    (empurra o tspan pra fora da tela); (2) `dominant-baseline="middle"/
    "central"` num `<text>` com `<tspan>` filho é recalculado *por sub-run* no
    Safari/iOS (WebKit) usando as métricas de cada tspan separadamente, em vez
    do texto inteiro como uma peça só — na prática deslocava só o "PB" (dentro
    do tspan) pra cima em relação a "Desert" no mobile, mesmo os dois usando a
    mesma fonte/tamanho (bug relatado por usuários, sem reprodução no
    desktop). `text-anchor="start"` e a baseline padrão ("alphabetic", sem
    nenhum `dominant-baseline`) não têm essa ambiguidade em nenhum
    renderizador — nenhum dos dois deixa a marca refém desse tipo de
    comportamento por-navegador.
  - Contorno branco grosso (`stroke-width: 3`, `paint-order="stroke"` — o
    traço é pintado *atrás* do preenchimento; sem isso, o traço centralizado
    no contorno da letra "come" metade da própria tinta e afina hastes finas)
    e uma sombra projetada em SVG (`<filter id="wordmark-shadow"><feDropShadow
    ...>`, aplicada só ao grupo do texto). Contorno + sombra é o que garante
    contraste contra qualquer fundo — nenhuma moldura/placa atrás do texto
    (foi tentado, ver "Jumbotron" abaixo, e descartado). O SVG é estático
    (`<img>`, sem acesso a `data-theme`), então essa combinação precisa
    funcionar sozinha nos dois temas sem poder trocar de cor.

**Não editar os `.svg`/`.ico` manualmente** — regenerar com
`python scripts/generate_logo.py` (lê `limite_semiarido_pb` e `ivd_sab` do
GeoPackage + as faixas de `styles.json`; precisa de `cairosvg`, `cairocffi` e
`Pillow` instalados — `cairocffi` normalmente já vem junto como dependência do
`cairosvg`) sempre que o contorno do semiárido ou os dados/faixas do IVD
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
"Marca" acima) — **sem** nenhuma forma com borda/edge atrás dele. Depois
disso, `.hero-mark-glow` foi adicionado atrás do **ícone+wordmark inteiro**
(não só o texto): um `radial-gradient` bem grande (`inset: -20% -14%`) e sem
nenhuma borda, só escurecendo levemente a foto ao redor da logo com uma
transição suave até transparente — não é a mesma coisa que as
pílulas/molduras rejeitadas (que tinham uma borda/edge visível); é
propositalmente discreto. Se for ajustar esse elemento, manter essa
diferença: nada de `border`, `box-shadow` com edge definida, ou
`backdrop-filter`.

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

Em `SobreView.vue`, o array `team` usa a presença do campo `tag` pra marcar o
coordenador do projeto — `coordinator = team.find((m) => m.tag)` /
`members = team.filter((m) => !m.tag)` — e não a posição no array. Ele
ganha um card próprio centralizado (`.team-lead`) acima da grade 2 colunas
dos demais. Só um membro deve ter `tag` preenchido; adicionar `tag` a mais
de um quebra esse split (`find` só pega o primeiro).

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
| 30–43 | "Indicadores de Vulnerabilidade" — raw data behind the Escores (Climáticos, Solo, Vegetação, Manejo), ordered by category |
| 50+ | Administrative boundaries (always on top) |

> Administrative boundaries were renumbered from 32–36 to 52–56 when the
> "Indicadores de Vulnerabilidade" branch was added, to keep them "always on
> top" while leaving room for the 14 new raw-indicator layers at 30–43.
> `focos_queimadas` is the one exception to this whole table — it doesn't use
> MVT tiles at all, so its `zIndex: 40` is only a sidebar-ordering
> convenience; actual stacking comes from rendering in Leaflet's
> `markerPane` (z-index 600), always above `tilePane` (z-index 200) where
> every other layer here lives, regardless of its `zIndex` number. See
> "Focos de Queimada" below.

---

## Existing layers (current state)

All layers cover the **Paraíba semi-arid region (Semiárido da PB)**, except
`limite_do_semiarido_br`, which outlines the wider Brazilian semi-arid region. They
come from the full information tree — IVD → Índices de Vulnerabilidade →
IVS/IVV/IVC/IVM → Escores de Vulnerabilidade, plus the raw data behind those
Escores in the "Indicadores de Vulnerabilidade" branch (Indicadores
Climáticos/de Solo/de Vegetação/de Manejo) — delivered and wired into the app
in 2026-07-31.

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
| `indice_aridez_semiarido_pb` | Indicadores Climáticos | Aridity index — raw value |
| `precipitacao_semiarido_pb` | Indicadores Climáticos | Rainfall — raw value (mm) |
| `eto_semiarido_pb` | Indicadores Climáticos | Evapotranspiration — raw value (mm) |
| `solos_textura` | Indicadores de Solo | Soil texture — categorical (string), not the numeric score |
| `tipos_solo` | Indicadores de Solo | Soil type / pedological component — categorical (string) |
| `declividade` | Indicadores de Solo | Slope — raw value (%), graduated into 6 classes (Plano → Escarpado) |
| `geologia` | Indicadores de Solo | Lithological type — categorical (string), 55 classes |
| `ndvi` | Indicadores de Vegetação | NDVI (May/2022) — categorized by `peso`, already pre-dissolved into 5 classes upstream (not a per-pixel layer) |
| `carbono_organico` | Indicadores de Vegetação | Soil organic carbon — raw value (g/kg) |
| `sucetibilidade_erosao` | Indicadores de Vegetação | Water erosion susceptibility — raw value |
| `focos_queimadas` | Indicadores de Manejo | Fire outbreak points (511 pts) — `Point` geometry, no attributes, served as static GeoJSON (not MVT), always rendered above every other layer |
| `dd_rural_2022_sab_pb` | Indicadores de Manejo | Rural demographic density (2022) — raw value (hab/km²) |
| `pressao_animal` | Indicadores de Manejo | Animal pressure (2017) — raw value (UA/ha) |
| `idhm_2010_sab_pb` | Indicadores de Manejo | Municipal HDI (2010) — raw value |

Every "Indicadores de Vulnerabilidade" leaf sits alongside its "Escores de
Vulnerabilidade" counterpart under a **different** category — e.g. both
`geologia_escores_de_vulnerabilidade` (IVS) and `geologia` (Indicadores de
Solo) render as `label: 'Geologia'` in the sidebar. This is intentional (it
mirrors the source `Projeto_QGIS` tree) — the parent category disambiguates
them, not the label. Same pattern for `focos_queimadas` ("Focos de Queimada"
under IVM escores vs. under Indicadores de Manejo), `declividade`,
`precipitacao_semiarido_pb`, etc.

> **`sourceLayer` here is the real GeoPackage table name, which for four of
> these layers differs from the name used in the original project
> documentation/QGIS project tree** — the delivery renamed the table but left
> a stale style row in `layer_styles` under the old name:
> `declividade` (not `declividade_semiarido_pb`), `geologia` (not
> `geologia_tipos_litologicos`), `ndvi` (not `ndvi_maio_2022`), `pressao_animal`
> (not `pressao_animal_sab_pb`). `scripts/styles.py`'s `RENAMED_TABLES` dict
> maps the stale style-row name to the real table (see Step 4) — if a future
> GeoPackage delivery renames a table again, add it there rather than hunting
> for why a layer silently has no style.

**`focos_queimadas` is the app's first and only layer NOT served as MVT
tiles.** It's a `Point` layer with **no attribute fields at all** and only
511 features — light enough to fetch as a single static GeoJSON file instead
of a `{z}/{x}/{y}.pbf` tile pyramid. See "Focos de Queimada" below for the
full architecture (`layers.js`'s `renderAs: 'geojson'`, where the file lives,
how it's deployed, and why it's always on top).

`focos_queimadas` is `noPopup: true` in `layers.js` (nothing to show) and a
`"single"`-type manual entry in `styles.json`, not a QML-extracted style
(same reason as the boundary layers below — `singleSymbol` QGIS renderers are
always skipped by the auto-extraction in `styles.py`).

**`solos_textura`, `tipos_solo` and `geologia` classify by text, not
number** (QGIS `categorizedSymbol` on a string field — soil texture name,
pedological component, lithology). `scripts/styles.py` keeps the class
`value` as the original string when it can't parse as a float (instead of
dropping the category); `scripts/geo_utils.py` (`classify_categorized`) and
`src/utils/mapRenderer.js` (`getThematicColor`) both branch on
`typeof classes[0].value === 'string'` to do an exact case-insensitive
string match instead of the numeric closest-value match used by every other
`categorized` layer.

**`solos_textura` had a QML field-name casing bug** — the QGIS style
referenced `DSC_TEXTUR` but the real GeoPackage column is lowercase
(`dsc_textur`), which SQLite tolerates (case-insensitive lookups) but the
GeoJSON/MVT export does not (preserves real casing) — `style.field` would
have silently never matched `feature.properties`, coloring the whole layer
gray. `scripts/styles.py` (`real_field_name`) resolves the QML `attr` to its
real casing via `PRAGMA table_info` before writing `styles.json`, for every
layer (not just this one) — cheap and always correct, so it's not
conditional on knowing in advance which layers have the bug.

**`declividade`'s classification is graduated (field `dn`, % slope) with 6
classes extracted straight from the QML** (Plano 0–3%, Suave Ondulado 3–8%,
Ondulado 8–20%, Forte Ondulado 20–45%, Montanhoso 45–75%, Escarpado >75%) —
a 7-class table with different boundaries and explicit weights (1.0–2.0) was
also considered (typed from memory, not from the GeoPackage) but the QML is
the authoritative source per the project's own convention ("always re-run
Step 4 rather than hand-editing `styles.json`"), so no manual override was
added. If the classification needs to change, edit it in QGIS and re-run
Step 4 — don't hand-edit `declividade` in `styles.json`.

**`municipios_pb_semiarido`, `limite_semiarido_pb`, `estados_ne` and `limite_do_semiarido_br`
are stroke-only** — their entries in `src/assets/styles.json` must use `"type": "stroke"`
(see the Styles section below for the full schema). All four also set `noPopup: true`
in `layers.js` (except `municipios_pb_semiarido`, which has a real popup) — they're pure
boundary outlines with no attributes worth surfacing in a popup, and being stroke-only
they're automatically skipped by `stats.py` so no chart button appears either.

---

## Focos de Queimada — a exceção arquitetural (GeoJSON, não MVT)

`focos_queimadas` é a única camada do app que **não** segue o pipeline de
vector tiles — decisão deliberada, não um atalho temporário:

- **Por quê**: é a única camada de pontos do projeto, sem nenhum atributo,
  511 feições — um `.geojson` inteiro (~62 KB) é mais barato de buscar de
  uma vez do que uma pirâmide `{z}/{x}/{y}.pbf` fatiada por zoom/tile.
- **Onde o arquivo vive**: `public/tiles/insa_layers/focos_queimadas.geojson`
  — dentro da MESMA pasta da pirâmide de tiles (não `public/data/`, onde
  fica `municipios_pb_semiarido.geojson`), de propósito: `npm run
  deploy:tiles` já compacta e envia essa pasta inteira pro servidor, então
  o arquivo viaja automaticamente sem precisar tocar em
  `scripts/deploy-tiles.sh`. Cai em produção em
  `https://sistema.sigrural.com.br/tiles/insa_layers/focos_queimadas.geojson`.
  Gitignored, igual ao resto de `public/tiles/` — **não** versionado (ao
  contrário de `municipios_pb_semiarido.geojson`, que é pequeno e estável o
  bastante pra viver no git).
- **Como é gerado**: `ogr2ogr -f GeoJSON public/tiles/insa_layers/focos_queimadas.geojson
  data/dados_insa.gpkg focos_queimadas -t_srs EPSG:4326` — roda **depois**
  do Step 3 (que faz `rm -rf public/tiles/insa_layers`, apagando esse
  arquivo junto com os tiles) e **fora** do comando do Tippecanoe no Step 2
  (`focos_queimadas` não entra nesse comando).
- **`layers.js`**: `renderAs: 'geojson'` no objeto da camada é o que
  diferencia esse leaf de todos os outros (que usam MVT por padrão, sem
  precisar de nenhum campo especial). `url` aponta pra
  `FOCOS_QUEIMADAS_URL`, derivada de `VECTOR_TILES_URL`
  (`.replace()` tira o sufixo `/{z}/{x}/{y}.pbf` e troca por
  `/focos_queimadas.geojson`) — não uma env var nova.
- **`MapContainer.vue`**: `syncVectorOverlays()` ramifica em
  `renderAs === 'geojson'` — `fetch` + `L.geoJSON` com `pointToLayer`
  retornando `L.circleMarker`, em vez de `CustomMVTLayer`. A camada some por
  padrão em `L.circleMarker`.
- **"Sempre acima das outras camadas" sai de graça, sem z-index especial**:
  `L.circleMarker` cai por padrão no `markerPane` do Leaflet (z-index 600).
  Toda `CustomMVTLayer` (`L.GridLayer`) das outras camadas vive no
  `tilePane` (z-index 200) — abaixo do `markerPane` sempre, não importa o
  `zIndex` numérico de nenhuma delas. Não foi criado nenhum pane customizado
  nem lógica de z-index adicional.
- **Opacidade**: o watcher genérico de opacidade em `MapContainer.vue` chama
  `.redraw()` em toda camada ativa — método que só existe em `L.GridLayer`,
  não em `L.GeoJSON`. A camada do focos_queimadas recebe um `.redraw` "shim"
  (atribuído na hora da criação) que reaplica o estilo em cada
  `circleMarker` via `.setStyle()`, pra continuar funcionando com esse
  watcher sem precisar de um caso especial lá.
- **Corrida fetch vs. toggle**: como a camada só entra em `activeOverlays`
  depois que o `fetch` resolve (assíncrono, diferente do MVT que registra a
  camada de forma síncrona antes de buscar tiles), o callback confere
  `mapStore.visibleOverlays[key]` antes de adicionar ao mapa — sem isso, uma
  camada desligada rápido o bastante (antes do fetch terminar) reapareceria
  sozinha quando o fetch finalmente resolvesse.
- **`geoJsonLayerCache`** (módulo-level `Map`, ao lado de `activeOverlays`):
  a camada Leaflet já montada (fetch + parse + os 511 `L.circleMarker`) é
  reaproveitada entre toggles — desligar e religar não refaz o fetch nem
  recria os markers, só chama `.addTo(map)`/`map.removeLayer()` na mesma
  instância. O GeoJSON é estático (não muda entre toggles), então não há
  risco de mostrar dado desatualizado.

---

## Data pipeline (GeoPackage → vector tiles)

> ⚠️ Every time a layer is added, removed, or changed in the GeoPackage,
> **all steps below must be re-run from scratch**. There is no partial update.
> Always delete `public/tiles/insa_layers/` before re-extracting.

Todos os comandos rodam a partir da **raiz do projeto**. Os scripts Python ficam
em `scripts/` e resolvem os paths automaticamente via `Path(__file__).parent.parent`.

### Manutenção do GeoPackage (`scripts/gpkg_dissolve_and_fix.py`)

Script em PyQGIS (`native:fixgeometries` + `native:dissolve`, precisa do
ambiente Python do QGIS — ver docstring do script) que roda **antes** do
pipeline abaixo, direto em `data/dados_insa.gpkg`, pra reduzir o tamanho do
arquivo: corrige geometrias inválidas e funde (`dissolve`) feições que
compartilham os mesmos valores em todos os seus campos — nunca muda nome,
tipo ou ordem de campo nenhum, só reduz feições redundantes (ex.
`ivs`: 16825→65 feições, mesmo conjunto de valores). Fica de fora do dissolve
(`EXCLUDE_LAYERS` no script) `municipios_pb_semiarido`, `estados_ne`,
`limite_semiarido_pb`, `limite_do_semiarido_br` (cada feição precisa
continuar endereçável individualmente pela aplicação) e `focos_queimadas`
(camada de pontos sem campo de atributo). Já rodado uma vez em 2026-07-31,
89,3 MB → 65,9 MB; backup do estado anterior ficou em
`data/dados_insa.antes-dissolve.gpkg` (gitignored, como o próprio `.gpkg`).
Não muda nada relevante pro Step 4/5/6 abaixo (`styles.py`/`stats.py`/
`dashboard_stats.py` classificam por valor/faixa, não por identidade de
feição, então área e classes calculadas continuam as mesmas).

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
  --no-tiny-polygon-reduction \
  --force \
  data/geojson/*.geojson
```

> ⚠️ **`--no-tiny-polygon-reduction` é obrigatório.** Sem essa flag, o
> Tippecanoe funde/derruba por padrão polígonos pequenos demais pra ocupar
> um pixel nos zooms baixos (comum em município com pouca área, ou num
> polígono de classe rara/pequena) — a feição simplesmente não existe mais
> naquele tile, com qualquer atributo que carregava junto. Isso não é só um
> problema visual: a busca (`matchesFilter` em `mapRenderer.js`) só enxerga
> o que está no tile que o navegador buscou, então uma feição derrubada
> nunca aparece como resultado, mesmo existindo no GeoPackage — foi
> exatamente o bug reportado em `pressao_animal` (`ua_ha_2017 >= 2`
> retornava "Nenhum resultado encontrado" mesmo com 1 feição em 2,53; sem
> essa flag o tile z2 tinha 198 das 207 feições, faltando bem o valor
> máximo). Confirmado reproduzindo local: com a flag, 207/207 presentes.

> Um glob (`data/geojson/*.geojson`) em vez de listar cada camada — mais
> simples de manter com 36 camadas, e `data/geojson/` só existe pra isso
> mesmo (regenerado do zero a cada rodada do pipeline, Step 1 sempre exporta
> exatamente as camadas certas). **Exceção:** `focos_queimadas.geojson`
> nunca é exportado pra `data/geojson/` — não passa pelo Tippecanoe, vai
> direto pra `public/tiles/insa_layers/` (ver "Focos de Queimada" acima).
> `layer_styles.geojson` é a tabela de estilos do QGIS — precisa estar em
> `data/geojson/` (entra no comando via glob) mas nunca é registrada como
> camada da aplicação.

> The `.mbtiles` file is ~200 MB (down from ~920 MB before
> `scripts/gpkg_dissolve_and_fix.py` — see "Manutenção do GeoPackage" above)
> — it is gitignored. Do not commit it. `public/tiles/insa_layers/` is
> correspondingly ~1.7 GB / ~420k `.pbf` files on disk (plus the one
> `focos_queimadas.geojson`).

### Step 3 — Delete old tiles and re-extract

```bash
rm -rf public/tiles/insa_layers      # MANDATORY — never skip this
python scripts/export.py             # writes public/tiles/insa_layers/{z}/{x}/{y}.pbf

# focos_queimadas não passa pelo Tippecanoe/export.py (ver "Focos de
# Queimada" acima) — o rm -rf acima apaga o .geojson dele junto com os
# tiles, então regenerar por último, depois do export.py:
ogr2ogr -f GeoJSON public/tiles/insa_layers/focos_queimadas.geojson \
  data/dados_insa.gpkg focos_queimadas -t_srs EPSG:4326
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

`styles.py` also resolves two known GeoPackage-delivery quirks automatically
(no manual step needed for either):

- **Case-insensitive field-name resolution** (`real_field_name`, via
  `PRAGMA table_info`) — a QML that references a column with different
  casing than the real GeoPackage column (SQLite tolerates it, the
  GeoJSON/MVT export doesn't) gets silently remapped to the real casing.
- **Stale-named style rows** (`RENAMED_TABLES` dict) — a few `layer_styles`
  rows still reference a table name from a previous GeoPackage delivery
  that no longer exists (e.g. `geologia_tipos_litologicos`, when the real
  table today is `geologia`). Add an entry there if a future delivery
  renames a table again and its style stops showing up.

String-categorized layers (`solos_textura`, `tipos_solo`, `geologia` — QGIS
`categorizedSymbol` on a text field) are captured automatically too — the
category `value` is kept as the original string instead of being dropped
when it can't parse as a float (see "Existing layers" above for how the
frontend/`stats.py` match on it).

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
> },
> "focos_queimadas": {
>   "type": "single",
>   "field": null,
>   "classes": [
>     { "label": "Foco de queimada", "color": "#ff0017" }
>   ]
> }
> ```
>
> `focos_queimadas` (`Point`, no attribute fields) is `singleSymbol` in QGIS —
> `styles.py` extracts its color correctly but always skips writing
> `singleSymbol` layers automatically (same as the stroke-only boundaries
> above), so it needs this manual entry too.

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

### Step 7 — Generate the search index

```bash
python scripts/search_index.py    # writes src/assets/search_index.json
```

Veja "Índice de busca" abaixo para o racional completo — resumindo, precisa
ser rodado sempre que o GeoPackage mudar (mesma regra do resto do pipeline),
já que é lido direto de `data/dados_insa.gpkg`, não derivado de nenhum
`.json` gerado por outro step.

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
      (Step 2's Tippecanoe command reads `data/geojson/*.geojson` via glob — no need to list the new file by name,
      **unless** the layer is a GeoJSON-exception like `focos_queimadas`, see "Focos de Queimada" above)
- [ ] Re-run Step 2 (generate `.mbtiles`)
- [ ] Re-run Step 3 (`rm -rf public/tiles/insa_layers` + `python scripts/export.py`)
- [ ] Re-run Step 4 (`python scripts/styles.py`)
- [ ] Restore any manual entries in `src/assets/styles.json` (styles.py overwrites the file — see warning above)
- [ ] If stroke-only, add entry manually to `src/assets/styles.json`
- [ ] Re-run Step 5 (`python scripts/stats.py`) to update `src/assets/stats.json`
- [ ] If the changed layer is one of the 5 composite indices (`ivs`/`ivv`/`ivc`/`ivm`/`ivd_sab`),
      also re-run Step 6 (`python scripts/dashboard_stats.py`)
- [ ] Re-run Step 7 (`python scripts/search_index.py`) to update `src/assets/search_index.json` —
      needed for the new layer's search to find matches outside the current viewport

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
   to `featureProps[style.field]` (QGIS "Categorized" symbology) — unless
   `classes[0].value` is a `string` (see below), in which case it does an
   exact case-insensitive string match instead.
2. **`graduated`** — range match: first class whose `max` (upper bound) is
   `>= featureProps[style.field]` (QGIS "Graduated" symbology).
3. **`stroke` / `single`** — fixed color, no attribute lookup (e.g. municipal
   boundaries, `focos_queimadas`).

Getting `categorized` vs `graduated` wrong produces a legend that *looks*
plausible (colors still render) but shows synthesized numeric ranges instead
of the real QGIS class labels — always re-run Step 4 after any style change
in QGIS rather than hand-editing `styles.json`.

**String-categorized layers** (`solos_textura`, `tipos_solo`, `geologia`) are
`categorized` but classify on text, not a number — `scripts/stats.py` →
`classify_categorized` (in `geo_utils.py`) mirrors the same string-vs-number
branch so area stats stay consistent with what's rendered on the map.

`drawGeometryToContext(ctx, geom, featureType, tileSize)` draws polygons
(`featureType === 3`, closes the path) and lines (`featureType === 2`) via
`moveTo`/`lineTo`. `focos_queimadas` doesn't go through this function at
all — it's rendered as `L.circleMarker` via Leaflet's own GeoJSON layer, not
painted on an MVT tile canvas (see "Focos de Queimada" above).

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

Duas coisas diferentes acontecem quando um filtro está ativo numa camada, e
usam fontes de dados diferentes:

1. **Destaque visual no mapa** (`MapContainer.vue`, dentro de `createTile`) —
   continua lendo os tiles MVT normalmente, tile por tile, conforme eles são
   buscados pra renderizar. Isso é inerente e correto: só dá pra pintar o que
   está na tela. Feições que não batem com o filtro ficam acinzentadas
   (`#6b7280`, baixa opacidade); as que batem mantêm a cor temática normal,
   sem nenhum destaque adicional.
2. **Contagem de resultados / badge "Nenhum resultado encontrado"**
   (`countFilterMatches`) — **não** usa os tiles renderizados, usa
   `src/assets/search_index.json` (ver "Índice de busca" abaixo). Isso é
   proposital, não só uma otimização: contar via tiles renderizados faria a
   busca depender do que por acaso já foi carregado na viewport atual — uma
   feição real que bate com o filtro, mas está fora da área/zoom visível no
   momento da busca, nunca seria vista, e o usuário veria "Nenhum resultado"
   pra uma busca que na verdade tem resultado em outro lugar do mapa.

---

## Índice de busca (`src/assets/search_index.json`)

Gerado por `scripts/search_index.py` — os valores de atributo (sem geometria)
de **toda** feição de **toda** camada espacial do GeoPackage, direto via
SQLite (não passa por GeoPandas nem pelos tiles MVT). Schema:

```json
{
  "ivd_sab": [ { "ivd": 1.42 }, { "ivd": 1.58 }, ... ],
  "municipios_pb_semiarido": [ { "nm_municip": "Sousa", "cod_ibge_m": "2515500", "slug": "sousa" }, ... ],
  "focos_queimadas": []
}
```

- Chave = `sourceLayer` (mesma convenção do resto do pipeline). Uma camada
  sem nenhum campo de atributo (`focos_queimadas`) aparece com array vazio,
  não fica ausente da chave — `searchIndex[sourceLayer] ?? []` no frontend
  não precisa se preocupar com a diferença.
- `countFilterMatches` em `MapContainer.vue` roda `matchesFilter` (mesma
  função de `mapRenderer.js` usada pro destaque visual) contra cada linha —
  garante que a lógica de comparação (operadores numéricos, substring
  case-insensitive) seja idêntica entre "o que pinta de cinza" e "o que conta
  como resultado", só a fonte dos dados é diferente.
- **Por que não um fetch dedicado de tile em zoom baixo, mais simples**: foi
  tentado — buscar só o tile z2 que cobre o Semiárido PB inteiro (a região
  inteira cabe numa tile só nesse zoom). Funciona pras camadas pequenas, mas
  camadas densas (`ivd_sab`, ~9,7 mil polígonos) perdem uma fração real de
  feições nesse zoom — não é um bug do Tippecanoe pra corrigir com flag
  nenhuma, é física de vetor tile: representar milhares de polígonos
  pequenos dentro da resolução de coordenadas de uma tile (4096 unidades)
  cobrindo um estado inteiro necessariamente colapsa algumas geometrias.
  `search_index.json` não tem esse problema porque não carrega geometria
  nenhuma — só os valores de atributo, então não existe zoom/resolução que
  degrade.
- **Compacto, sem `indent`** (diferente de `styles.json`/`stats.json`) —
  gerado e consumido só por código, nunca editado à mão, e `ivd_sab` sozinho
  tem quase 10 mil linhas.
- **Tamanho**: ~220 KB hoje (37 camadas, ~12 mil feições ao todo — a maior
  parte é `ivd_sab`, que tem só 1 campo numérico por feição). Importado
  estaticamente em `MapContainer.vue`, então entra no bundle do `/mapa`
  (rota já é o núcleo da aplicação, carregar isso ali é a troca certa —
  correção da busca vale mais que raspar ~68 KB gzip de um bundle que o
  usuário já vai carregar pra usar o mapa de qualquer forma).
- Regenerar sempre que o GeoPackage mudar (Step 7 do pipeline) — não deriva
  de nenhum outro `.json` gerado, lê direto de `data/dados_insa.gpkg`.

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
- Do not add `focos_queimadas.geojson` to the Tippecanoe command in Step 2 or
  export it to `data/geojson/` — it's the one layer that deliberately skips
  the MVT pipeline entirely (see "Focos de Queimada" above); it's generated
  straight into `public/tiles/insa_layers/` with its own `ogr2ogr` call,
  after Step 3 (whose `rm -rf` would otherwise delete it)
- Do not give a new layer `renderAs: 'geojson'` in `layers.js` just because
  it's small — that flag also skips the tile pyramid, MVT search/filter,
  and popup-by-click infrastructure entirely; it only makes sense for a
  layer with no attributes and few enough features to fetch in one request
- Do not make `countFilterMatches` in `MapContainer.vue` scan `tileDataCache`
  (rendered tiles) again — that was the original bug: match counting only
  saw whatever tiles happened to already be on screen, missing real matches
  outside the current viewport/zoom. It reads `search_index.json` now (see
  "Índice de busca" above) precisely to not depend on what's rendered.
- Do not remove `--no-tiny-polygon-reduction` from the Tippecanoe command in
  Step 2 — without it, small polygons get merged/dropped at low zoom by
  default, silently removing features (and whatever attribute value they
  carried) from those tiles. Caused a real bug: searching `pressao_animal`
  for its own maximum value returned no results, because that one feature's
  tile at low zoom didn't have it anymore.
- Do not forget Step 7 (`python scripts/search_index.py`) when regenerating
  the pipeline after a GeoPackage change — unlike `stats.json`, it isn't
  derived from `styles.json`, so nothing else in the pipeline will remind
  you it's stale
  (today, only `focos_queimadas` qualifies)

---

## Session startup ritual

At the beginning of each session, run:

```bash
git log --oneline -10
```

Then read this file and `src/config/layers.js` to understand the current state
before making any changes.