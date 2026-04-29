# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev        # Development server (Vite)
npm run build      # Production build
npm run preview    # Preview production build
npm run lint       # Run oxlint + eslint with auto-fix (sequential)
npm run format     # Prettier format src/
```

No test suite is configured.

## Architecture

Vue 3 GIS web mapping application (JavaScript, not TypeScript) using Vite. Connects to a local GeoServer instance at `http://localhost:8080/geoserver/insa/wms` for WMS tile layers.

**Data flow for map layers:**

1. `src/stores/mapStore.js` — Pinia store is the single source of truth for all layer state: which base layer is active (OSM or ESRI Satellite) and visibility of each WMS overlay.
2. `src/views/HomeView.vue` — Renders the sidebar with radio buttons (base layers) and checkboxes (overlays). Mutates the store directly.
3. `src/components/MapContainer.vue` — Owns the Leaflet instance. Watches the Pinia store reactively and applies changes to the map (swaps base tile layers, adds/removes WMS overlays). Never holds its own layer state.

**Key design constraint:** Leaflet cannot be rendered server-side. `MapContainer.vue` initializes the Leaflet map in `onMounted` and cleans it up in `onUnmounted`. Do not access `L` or the map instance outside these lifecycle hooks.

**WMS layers** are defined in `mapStore.js` as an array of overlay objects with `{ id, name, wmsLayer, visible }`. Adding a new GeoServer layer means adding an entry to that array — the map component handles rendering automatically via the reactive watcher.

## Stack

- Vue 3 (Composition API, `<script setup>`)
- Pinia for state management
- Leaflet 1.x for map rendering
- Bootstrap 5 for layout/UI
- FontAwesome 7 (tree-shaken — only import icons that are registered in `src/main.js`)
- Oxlint + ESLint + Prettier for code quality

## GeoServer dependency

The app requires a running GeoServer at `http://localhost:8080/geoserver/insa/wms`. Without it, WMS overlays will fail silently (Leaflet tiles 404). The base tile layers (OSM, ESRI) work without GeoServer.
