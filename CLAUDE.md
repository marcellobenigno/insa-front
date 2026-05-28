# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.
Read it fully at the start of every session before making any changes.

---

## Project overview

WebGIS application for INSA (Instituto Nacional do Semiárido) displaying thematic
vector layers over the Paraíba semi-arid region (Semiárido da PB). Built with
Vue 3 + Vite. Serves vector tiles locally from `public/tiles/` — there is no
external map server dependency at runtime.

---

## Commands

```bash
npm run dev        # Development server with hot-reload (Vite)
npm run build      # Production build → dist/
npm run preview    # Preview production build
npm run lint       # oxlint + eslint with auto-fix (sequential)
npm run format     # Prettier format on src/
```

No test suite is configured.

---

## Stack

| Layer | Library |
|---|---|
| UI framework | Vue 3 — Composition API, `<script setup>` — JavaScript, NOT TypeScript |
| State | Pinia (`src/stores/mapStore.js`) |
| Map | Leaflet 1.x |
| Vector tiles | `leaflet.vectorgrid` (Leaflet plugin) |
| Layout / UI | Bootstrap 5 |
| Icons | Bootstrap Icons 1.x — loaded via CDN in `index.html` (no npm package) |
| Linting | Oxlint + ESLint + Prettier |

---

## Architecture

### Data flow

```
src/config/layers.js          ← SINGLE SOURCE OF TRUTH for layer definitions
        ↓
src/stores/mapStore.js        ← Pinia: reactive state (active base layer, overlay visibility/opacity)
        ↓
src/components/AppSidebar.vue ← reads + mutates store; renders layer controls
src/components/LayerCard.vue  ← per-layer card (toggle, opacity slider, legend)
        ↓
src/components/MapContainer.vue ← owns Leaflet instance; watches store; applies changes to map
```

Other components (not part of the layer flow):

- `GeoSearch.vue` — geocoding / coordinate search (address, DD, DMS); pans the map via the store
- `CoordDisplay.vue` — real-time cursor coordinates overlay (DD and DMS)

### Key design constraints — NEVER violate these

1. **Leaflet is client-only.** Initialize the map in `onMounted`, destroy in `onUnmounted`.
   Never access `L` or the map instance outside these lifecycle hooks.

2. **`MapContainer.vue` owns no layer state.** It reads the store via watchers and
   applies changes to Leaflet. It never stores which layers are active internally.

3. **`src/config/layers.js` is the only place to define layers.**
   No layer configuration exists anywhere else in the application. Do not add
   layer logic to the store or the map component.

4. **`OVERLAY_LAYERS` is derived automatically** from `OVERLAY_CATEGORIES` inside
   `layers.js`. Never edit `OVERLAY_LAYERS` directly.

5. **`sourceLayer` must exactly match the layer name in the GeoPackage** (and the
   GeoJSON filename without extension used by Tippecanoe). Any divergence causes
   tiles to silently not render.

---

## Layer configuration reference (`src/config/layers.js`)

This is the **only file to edit** when adding, removing, or changing a layer.

### Structure

```js
export const BASE_LAYERS = { /* OSM, Satellite, etc. — radio-button selection */ }

export const OVERLAY_CATEGORIES = {
  category_key: {
    label: 'Label shown in accordion',
    color: '#hex',          // sidebar indicator color
    icon:  'bi-icon-name',  // Bootstrap Icons class
    layers: {
      layer_key: { /* see fields below */ }
    }
  }
}

// OVERLAY_LAYERS is auto-generated from OVERLAY_CATEGORIES — do not edit directly
```

### Layer object fields

```js
layer_key: {
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
}
```

### `zIndex` conventions

| Range | Use |
|---|---|
| 1 | Base tile layers |
| 10–19 | Indices and thematic data |
| 20–29 | Soils and texture |
| 30+ | Administrative boundaries (always on top) |

---

## Existing layers (current state)

All layers cover the **Paraíba semi-arid region (Semiárido da PB)**.
Each thematic variable has two variants: `_original` (raw values) and `_pesos` (weighted scores).

| `sourceLayer` | Description |
|---|---|
| `declividade_sab_pb` | Slope (processed) |
| `declividade_sab_pb_original` | Slope — raw values |
| `declividade_sab_pb_pesos` | Slope — weights |
| `eto_sab_pb_original` | Evapotranspiration — raw |
| `eto_sab_pb_pesos` | Evapotranspiration — weights |
| `geologia_sab_pb_original` | Geology — raw |
| `geologia_sab_pb_pesos` | Geology — weights |
| `ia_sab_pb_original` | Aridity index — raw |
| `ia_sab_pb_pesos` | Aridity index — weights |
| `iqc_sab_pb` | IQC — water quality index |
| `iqs_sab_pb` | IQS — soil quality index |
| `municipios_pb_semiarido` | Municipal boundaries (stroke-only) |
| `precipitacao_sab_pb_original` | Rainfall — raw |
| `precipitacao_sab_pb_pesos` | Rainfall — weights |
| `solos_tipos_sab_pb_original` | Soil types — raw |
| `solos_tipos_sab_pb_pesos` | Soil types — weights |
| `textura_sab_pb_original` | Soil texture — raw |
| `textura_sab_pb_pesos` | Soil texture — weights |

**`municipios_pb_semiarido` is stroke-only** — its entry in `src/assets/styles.json`
must use the `stroke:` prefix:

```json
"municipios_pb_semiarido": {
  "Limite municipal": "stroke:#ffffff"
}
```

---

## Data pipeline (GeoPackage → vector tiles)

> ⚠️ Every time a layer is added, removed, or changed in the GeoPackage,
> **all steps below must be re-run from scratch**. There is no partial update.
> Always delete `public/tiles/insa_layers/` before re-extracting.

All pipeline commands run from inside `data/`:

```bash
cd data/
```

### Step 1 — Export each layer from GeoPackage to GeoJSON

```bash
# List available layers
ogrinfo -q dados_insa.gpkg

# Export one layer (repeat for each)
ogr2ogr -f GeoJSON geojson/<layer_name>.geojson \
  dados_insa.gpkg <layer_name> \
  -t_srs EPSG:4326
```

### Step 2 — Generate `.mbtiles` with Tippecanoe

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

> `layer_styles.geojson` is the QGIS style table — include it in the command but
> do not register it as an application layer.

> The `.mbtiles` file is ~90 MB — it is gitignored. Do not commit it.

### Step 3 — Delete old tiles and re-extract

```bash
rm -rf ../public/tiles/insa_layers      # MANDATORY — never skip this
python3 export.py                        # writes public/tiles/insa_layers/{z}/{x}/{y}.pbf
```

### Step 4 — Extract styles

```bash
python3 styles.py    # writes src/assets/styles.json from layer_styles in the GeoPackage
```

If a layer is styled as stroke-only in QGIS (no fill), `styles.py` will not capture it.
Add the entry manually to `src/assets/styles.json` using the `stroke:` prefix.

### Required tools (macOS)

```bash
brew install gdal tippecanoe python3
```

---

## Checklist: adding a new layer

### Data side

- [ ] Add layer to `dados_insa.gpkg` in QGIS and save the style
- [ ] Export to GeoJSON: `ogr2ogr -f GeoJSON geojson/<layer>.geojson dados_insa.gpkg <layer> -t_srs EPSG:4326`
- [ ] Add the new `.geojson` to the Tippecanoe command in Step 2 (and update this file)
- [ ] Re-run Step 2 (generate `.mbtiles`)
- [ ] Re-run Step 3 (`rm -rf` + `python3 export.py`)
- [ ] Re-run Step 4 (`python3 styles.py`)
- [ ] If stroke-only, add entry manually to `src/assets/styles.json`

### Code side

- [ ] Add the layer object to the correct category in `src/config/layers.js`
- [ ] Set `sourceLayer` to exactly match the GeoPackage layer name
- [ ] If the layer has new field names not yet in `src/utils/mapRenderer.js → possibleValues`, add them

---

## Renderer (`src/utils/mapRenderer.js`)

Reads `src/assets/styles.json` and paints each feature on a canvas based on its
attribute values. When a new layer introduces field names not already listed in
`possibleValues`, add them so the renderer can match feature values to legend colors.

---

## Styles (`src/assets/styles.json`)

Auto-generated by `data/styles.py`. Structure:

```json
{
  "layer_name": {
    "Legend label": "#rrggbb",
    "Another label": "stroke:#rrggbb"
  }
}
```

- Plain hex `"#rrggbb"` → filled polygon
- `"stroke:#rrggbb"` → outline only, no fill

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
- Do not edit `OVERLAY_LAYERS` directly — it is derived from `OVERLAY_CATEGORIES`
- Do not commit `data/mbtiles/` or `data/geojson/` — both are gitignored due to size
- Do not run a partial pipeline update — always regenerate everything from scratch
- Do not assume `sourceLayer` is flexible — it must be byte-identical to the GeoPackage layer name

---

## Session startup ritual

At the beginning of each session, run:

```bash
git log --oneline -10
```

Then read this file and `src/config/layers.js` to understand the current state
before making any changes.