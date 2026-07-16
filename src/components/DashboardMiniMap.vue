<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { BASE_LAYERS, OVERLAY_LAYERS } from '@/config/layers'
import { createDashboardMvtLayer } from '@/utils/createDashboardMvtLayer'
import { useTheme } from '@/composables/useTheme'
import stylesJson from '@/assets/styles.json'

const props = defineProps({
  sourceLayer: { type: String, required: true },
  selectedMunicipio: { type: String, default: null }, // cod_ibge_m
})

const { isDark } = useTheme()
const mapEl = ref(null)

let map = null
let baseTileLayer = null
let indexLayer = null
let highlightedLayer = null
let layersControl = null
const municipiosByCod = new Map() // cod_ibge_m -> L.Layer

// Mesma área do mapa principal (MapContainer.vue) — duplicado aqui de
// propósito, são só 2 coordenadas, não lógica a compartilhar.
const paraibaBounds = [
  [-8.3, -38.76],
  [-6.02, -35.17],
]

const HIGHLIGHT_COLOR = '#fbbf24' // mesma cor de destaque usada em MapContainer.vue para matches de busca

const legendClasses = computed(() => stylesJson[props.sourceLayer]?.classes ?? [])

function currentBaseLayerConfig() {
  return isDark.value ? BASE_LAYERS.osm_dark : BASE_LAYERS.osm
}

function renderBaseLayer() {
  if (baseTileLayer) map.removeLayer(baseTileLayer)
  const { url, attribution, maxZoom } = currentBaseLayerConfig()
  baseTileLayer = L.tileLayer(url, { attribution, maxZoom, zIndex: 1 }).addTo(map)
}

function renderIndexLayer() {
  if (indexLayer) {
    map.removeLayer(indexLayer)
    layersControl?.removeLayer(indexLayer)
  }
  const layerConfig = OVERLAY_LAYERS[props.sourceLayer]
  if (!layerConfig) return
  indexLayer = createDashboardMvtLayer({
    url: layerConfig.url,
    sourceLayer: props.sourceLayer,
    opacity: 0.85,
    zIndex: 10,
  }).addTo(map)
  layersControl?.addOverlay(indexLayer, layerConfig.label ?? 'Índice')
}

function municipioBaseStyle() {
  const color = stylesJson.municipios_pb_semiarido?.classes?.[0]?.color ?? '#ffffff'
  return { color, weight: 1.2, opacity: 0.9, fillOpacity: 0 }
}

function municipioHighlightStyle() {
  return { color: HIGHLIGHT_COLOR, weight: 3.5, opacity: 1, fillOpacity: 0 }
}

async function loadMunicipiosGeoJson() {
  const url = `${import.meta.env.BASE_URL}data/municipios_pb_semiarido.geojson`
  const res = await fetch(url)
  const geojson = await res.json()
  if (!map) return // componente pode ter desmontado antes do fetch terminar

  const municipiosLayer = L.geoJSON(geojson, {
    style: municipioBaseStyle,
    onEachFeature: (feature, layer) => {
      municipiosByCod.set(feature.properties.cod_ibge_m, layer)
    },
  }).addTo(map)
  layersControl?.addOverlay(municipiosLayer, 'Municípios')

  applyHighlight(props.selectedMunicipio)
}

function applyHighlight(cod) {
  if (highlightedLayer) {
    highlightedLayer.setStyle(municipioBaseStyle())
    highlightedLayer = null
  }
  if (!cod) return
  const layer = municipiosByCod.get(cod)
  if (!layer) return
  layer.setStyle(municipioHighlightStyle())
  layer.bringToFront()
  highlightedLayer = layer
  // O painel do dashboard é montado via CSS grid/flex — o tamanho do container
  // pode não estar 100% assentado no primeiro fitBounds, e o Leaflet cacheia
  // esse tamanho internamente. invalidateSize() força a remedição antes de
  // calcular o zoom/centro do fitBounds, evitando um zoom incorreto.
  map.invalidateSize()
  // animate:false é essencial aqui: com animação, cliques sucessivos em
  // municípios diferentes podem interromper o voo (fly) do fitBounds anterior
  // no meio, deixando o mapa "preso" num zoom/centro intermediário errado
  // (foi isso que causava o problema relatado com Patos).
  map.fitBounds(layer.getBounds(), { padding: [40, 40], maxZoom: 11, animate: false })
}

function addZoomHomeControl() {
  const MiniZoomHomeControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control zoom-home-control')

      const zoomIn = L.DomUtil.create('button', 'zoom-btn', container)
      zoomIn.innerHTML = '<i class="bi bi-plus"></i>'
      zoomIn.title = 'Aproximar'
      L.DomEvent.on(zoomIn, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.zoomIn()
      })

      const home = L.DomUtil.create('button', 'zoom-btn home-btn', container)
      home.innerHTML = '<i class="bi bi-house"></i>'
      home.title = 'Voltar à visão inicial'
      L.DomEvent.on(home, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.invalidateSize()
        map.fitBounds(paraibaBounds, { animate: false })
      })

      const zoomOut = L.DomUtil.create('button', 'zoom-btn', container)
      zoomOut.innerHTML = '<i class="bi bi-dash"></i>'
      zoomOut.title = 'Afastar'
      L.DomEvent.on(zoomOut, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.zoomOut()
      })

      return container
    },
  })
  new MiniZoomHomeControl().addTo(map)
}

watch(() => props.sourceLayer, renderIndexLayer)
watch(isDark, renderBaseLayer)
watch(() => props.selectedMunicipio, applyHighlight)

onMounted(() => {
  // attributionControl fica ligado (default) — os tiles OSM/Carto do BASE_LAYERS
  // exigem atribuição visível, igual ao mapa principal.
  map = L.map(mapEl.value, { zoomControl: false }).fitBounds(paraibaBounds)
  map.setMaxBounds(paraibaBounds)
  map.setMinZoom(6)

  renderBaseLayer()
  // Controle nativo do Leaflet para ligar/desligar as camadas de sobreposição
  // (índice e contorno dos municípios) — sem base layers, só overlays.
  layersControl = L.control.layers(null, {}, { position: 'topright' }).addTo(map)
  renderIndexLayer()
  addZoomHomeControl()
  loadMunicipiosGeoJson()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
  municipiosByCod.clear()
})
</script>

<template>
  <div class="dashboard-mini-map">
    <div ref="mapEl" class="mini-map-canvas" />
    <div v-if="legendClasses.length" class="mini-map-legend">
      <div v-for="item in legendClasses" :key="item.label" class="legend-item">
        <span class="legend-swatch" :style="{ background: item.color }" />
        <span class="legend-item-label">{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-mini-map {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.mini-map-canvas {
  flex: 1;
  min-height: 280px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--btn-bg);
}

.mini-map-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 4px 2px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-swatch {
  flex-shrink: 0;
  width: 20px;
  height: 12px;
  border-radius: 4px;
}

.legend-item-label {
  font-size: 12px;
  font-weight: 400;
  letter-spacing: -0.12px;
  line-height: 1.4;
  color: var(--text-main);
}

/* ── Controle de zoom customizado (mesmo visual de MapContainer.vue) ────────── */
:deep(.zoom-home-control) {
  display: flex;
  flex-direction: column;
  border: none !important;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

:deep(.zoom-btn) {
  width: 30px;
  height: 30px;
  border: none;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  transition:
    background 0.15s,
    color 0.15s;
}

:deep(.zoom-btn:last-child) {
  border-bottom: none;
}

:deep(.zoom-btn:hover) {
  background: var(--bg-card-hover);
  color: var(--accent);
}

:deep(.home-btn) {
  font-size: 0.85rem;
  color: var(--text-dim);
}

/* ── Controle nativo de camadas (L.control.layers) — tema-aware ─────────────── */
:deep(.leaflet-control-layers) {
  border: 1px solid var(--border-color) !important;
  border-radius: 10px !important;
  background: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

:deep(.leaflet-control-layers-toggle) {
  width: 30px !important;
  height: 30px !important;
  border-radius: 10px;
}

:deep(.leaflet-control-layers-expanded) {
  padding: 10px 12px;
  color: var(--text-main);
  font-size: 12px;
}

:deep(.leaflet-control-layers-overlays label) {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0;
  cursor: pointer;
}

:deep(.leaflet-control-layers-separator) {
  border-top: 1px solid var(--border-color);
}
</style>
