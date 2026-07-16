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
const emit = defineEmits(['clear-selection'])

const { isDark } = useTheme()
const mapEl = ref(null)

let map = null
let baseTileLayer = null
let indexLayer = null
let highlightedLayer = null
let hoveredLayer = null
let layersControl = null
let hoverNameEl = null
// true só durante o fitBounds que o próprio applyHighlight dispara ao
// selecionar um município — sem isso, esse fitBounds geraria um 'movestart'
// que cancelaria a seleção que acabou de ser aplicada.
let suppressAutoDeselect = false
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

function municipioHoverStyle() {
  return { color: HIGHLIGHT_COLOR, weight: 2.5, opacity: 1, fillOpacity: 0.08 }
}

function setHoverName(name) {
  if (!hoverNameEl) return
  hoverNameEl.textContent = name ? `Município: ${name}` : ''
  hoverNameEl.classList.toggle('is-visible', !!name)
}

function handleMunicipioMouseOver(e) {
  const layer = e.target
  // Defesa contra 'mouseout' perdido em movimentos rápidos do mouse entre
  // polígonos vizinhos: se sobrou um hover anterior sem ter sido limpo,
  // reverte antes de aplicar o novo (evita múltiplos polígonos destacados
  // ao mesmo tempo). Não chamamos bringToFront() aqui de propósito — isso
  // reordena o SVG no DOM a cada hover e era a causa provável do 'mouseout'
  // não disparar de forma confiável em passadas rápidas.
  if (hoveredLayer && hoveredLayer !== layer && hoveredLayer !== highlightedLayer) {
    hoveredLayer.setStyle(municipioBaseStyle())
  }
  hoveredLayer = layer
  if (layer !== highlightedLayer) {
    layer.setStyle(municipioHoverStyle())
  }
  setHoverName(layer.feature?.properties?.nm_municip)
}

function handleMunicipioMouseOut(e) {
  const layer = e.target
  if (layer !== highlightedLayer) {
    layer.setStyle(municipioBaseStyle())
  }
  if (hoveredLayer === layer) {
    hoveredLayer = null
    setHoverName(null)
  }
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
      layer.on('mouseover', handleMunicipioMouseOver)
      layer.on('mouseout', handleMunicipioMouseOut)
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
  suppressAutoDeselect = true
  map.fitBounds(layer.getBounds(), { padding: [40, 40], maxZoom: 11, animate: false })
  suppressAutoDeselect = false
}

// Qualquer movimento do mapa iniciado pelo usuário (arrastar, zoom pelos
// botões, roda do mouse) — exceto o fitBounds que a própria seleção dispara,
// suprimido acima — limpa a seleção. Sem isso, o destaque amarelo e o zoom
// travado num município ficavam "grudados" mesmo depois do usuário navegar
// para outro lugar do mapa.
function handleUserMoveStart() {
  if (suppressAutoDeselect) return
  emit('clear-selection')
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

// Caixa fixa que mostra o nome do município sob o cursor — Leaflet empilha
// controles adicionados na mesma posição em ordem, então isso fica logo
// abaixo do controle de camadas (ambos em 'topright'). Precisa ser adicionada
// depois de layersControl para ficar embaixo dele na pilha.
function addHoverNameControl() {
  const HoverNameControl = L.Control.extend({
    options: { position: 'topright' },
    onAdd() {
      const container = L.DomUtil.create('div', 'leaflet-control municipio-hover-box')
      hoverNameEl = container
      return container
    },
  })
  new HoverNameControl().addTo(map)
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
  addHoverNameControl()
  loadMunicipiosGeoJson()
  map.on('movestart', handleUserMoveStart)
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
  municipiosByCod.clear()
  highlightedLayer = null
  hoveredLayer = null
  hoverNameEl = null
})
</script>

<template>
  <div class="dashboard-mini-map">
    <div class="mini-map-canvas-wrapper">
      <div ref="mapEl" class="mini-map-canvas" />
      <div v-if="legendClasses.length" class="mini-map-legend">
        <div class="mini-map-legend-title">Legenda</div>
        <div class="mini-map-legend-list">
          <div v-for="item in legendClasses" :key="item.label" class="legend-item">
            <span class="legend-swatch" :style="{ background: item.color }" />
            <span class="legend-item-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-mini-map {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mini-map-canvas-wrapper {
  position: relative;
  flex: 1;
  min-height: 280px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--btn-bg);
}

.mini-map-canvas {
  width: 100%;
  height: 100%;
}

/* ── Legenda flutuante sobre o mapa ───────────────────────────────────────────── */
.mini-map-legend {
  position: absolute;
  z-index: 1000;
  left: 10px;
  bottom: 10px;
  max-width: 200px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

.mini-map-legend-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-dim);
  margin-bottom: 8px;
}

.mini-map-legend-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
  max-height: 160px;
  overflow-y: auto;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.mini-map-legend-list::-webkit-scrollbar {
  width: 4px;
}
.mini-map-legend-list::-webkit-scrollbar-track {
  background: transparent;
}
.mini-map-legend-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 2px;
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
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15);
}

.legend-item-label {
  font-size: 11.5px;
  font-weight: 400;
  letter-spacing: -0.1px;
  line-height: 1.35;
  color: var(--text-main);
  word-break: break-word;
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

/* ── Caixa de nome ao passar o mouse no município ────────────────────────────── */
:deep(.municipio-hover-box) {
  max-width: 0;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  padding: 0;
  margin: 0 !important;
  border: none;
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-main);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
  pointer-events: none;
  transition: opacity 0.12s ease;
}

:deep(.municipio-hover-box.is-visible) {
  max-width: 300px;
  max-height: 32px;
  opacity: 1;
  padding: 7px 12px;
  margin-top: 10px !important;
  margin-right: 10px !important;
  border: 1px solid var(--border-color);
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
