<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapStore = useMapStore()
const mapEl = ref(null)

// ── Instâncias Leaflet (fora do sistema reativo) ───────────────────────────────
let map               = null
let currentTileLayer  = null
const wmsLayers       = new Map()

// ── GetFeatureInfo — estado interno ───────────────────────────────────────────
let highlightLayer       = null
let mouseMoveTimeout     = null
let hoverAbortController = null

onMounted(() => {
  const semiaridoBounds = [
    [-17.9954314609998995, -46.5772829000000002],
    [-2.6851430819999700,  -35.2625510709999972],
  ]

  map = L.map(mapEl.value).fitBounds(semiaridoBounds)
  renderTileLayer()
  syncOverlays(mapStore.visibleOverlays)

  map.on('click',     handleMapClick)
  map.on('mousemove', handleMouseMove)
  map.on('mouseout',  handleMouseOut)
})

onUnmounted(() => {
  if (map) {
    clearTimeout(mouseMoveTimeout)
    hoverAbortController?.abort()
    map.remove()
    map = null
  }
})

// ── Camada Base ───────────────────────────────────────────────────────────────

watch(() => mapStore.activeBaseLayer, renderTileLayer)

function renderTileLayer() {
  // Desestrutura campos não-Leaflet; o restante vai direto como opções
  const { url, label, meta, active, ...leafletOptions } = mapStore.activeBaseLayer
  const opacity = mapStore.layerOpacity[mapStore.activeBaseLayerKey] ?? 1
  if (currentTileLayer) map.removeLayer(currentTileLayer)
  // zIndex: 1 garante que o base layer fique sempre abaixo dos overlays WMS
  currentTileLayer = L.tileLayer(url, { ...leafletOptions, opacity, zIndex: 1 }).addTo(map)
}

// ── Camadas de Sobreposição (WMS) ─────────────────────────────────────────────

watch(
  () => mapStore.visibleOverlays,
  (desired) => { if (map) syncOverlays(desired) },
  { deep: true },
)

function syncOverlays(desired) {
  for (const { key, geoServerUrl, wmsLayer, attribution, maxZoom, minZoom, zIndex } of mapStore.availableOverlays) {
    const shouldBeVisible = desired[key]
    const isOnMap         = wmsLayers.has(key)

    if (shouldBeVisible && !isOnMap) {
      const opacity = mapStore.layerOpacity[key] ?? 1
      const layer = L.tileLayer
        .wms(geoServerUrl, { layers: wmsLayer, format: 'image/png', transparent: true, attribution, maxZoom, minZoom, opacity, zIndex })
        .addTo(map)
      wmsLayers.set(key, layer)
    } else if (!shouldBeVisible && isOnMap) {
      map.removeLayer(wmsLayers.get(key))
      wmsLayers.delete(key)
    }
  }
}

// ── Opacidade ─────────────────────────────────────────────────────────────────

watch(
  () => mapStore.layerOpacity,
  (opacities) => {
    const baseKey = mapStore.activeBaseLayerKey
    if (currentTileLayer && baseKey in opacities) currentTileLayer.setOpacity(opacities[baseKey])
    for (const [key, layer] of wmsLayers) {
      if (key in opacities) layer.setOpacity(opacities[key])
    }
  },
  { deep: true },
)

// ── GetFeatureInfo ────────────────────────────────────────────────────────────

function getInfoActiveLayers() {
  return mapStore.availableOverlays.filter(
    (l) => mapStore.infoActive[l.key] && mapStore.visibleOverlays[l.key],
  )
}

function buildGFIUrl(geoServerUrl, wmsLayer, latlng) {
  const point  = map.latLngToContainerPoint(latlng)
  const bounds = map.getBounds()
  const sw     = bounds.getSouthWest()
  const ne     = bounds.getNorthEast()
  const size   = map.getSize()

  const params = new URLSearchParams({
    SERVICE:       'WMS',
    VERSION:       '1.1.0',
    REQUEST:       'GetFeatureInfo',
    FORMAT:        'image/png',
    TRANSPARENT:   'true',
    LAYERS:        wmsLayer,
    QUERY_LAYERS:  wmsLayer,
    STYLES:        '',
    INFO_FORMAT:   'application/json',
    FEATURE_COUNT: '1',
    SRS:           'EPSG:4326',
    WIDTH:         size.x,
    HEIGHT:        size.y,
    BBOX:          `${sw.lng},${sw.lat},${ne.lng},${ne.lat}`,
    X:             Math.round(point.x),
    Y:             Math.round(point.y),
  })

  return `${geoServerUrl}?${params}`
}

async function fetchGFI(layer, latlng, signal = null) {
  try {
    const url = buildGFIUrl(layer.geoServerUrl, layer.wmsLayer, latlng)
    const res = await fetch(url, signal ? { signal } : {})
    if (!res.ok) return null
    const data = await res.json()
    return data.features?.[0] ?? null
  } catch (e) {
    if (e.name === 'AbortError') throw e
    return null
  }
}

// ── Clique — popup ────────────────────────────────────────────────────────────

async function handleMapClick(e) {
  const layers = getInfoActiveLayers()
  if (layers.length === 0) return

  const results = await Promise.allSettled(
    layers.map(async (l) => {
      const feat = await fetchGFI(l, e.latlng)
      return feat ? { label: l.label, feature: feat } : null
    }),
  )

  const hits = results
    .filter((r) => r.status === 'fulfilled' && r.value !== null)
    .map((r) => r.value)

  if (hits.length === 0) return

  L.popup({ className: 'popup-dark', maxWidth: 320 })
    .setLatLng(e.latlng)
    .setContent(buildPopupHtml(hits))
    .openOn(map)
}

function buildPopupHtml(hits) {
  const sections = hits
    .map(({ label, feature }) => {
      const rows = Object.entries(feature.properties ?? {})
        .filter(([, v]) => v != null && v !== '')
        .map(([k, v]) => `<tr><td class="gfi-key">${k}</td><td class="gfi-val">${v}</td></tr>`)
        .join('')

      return `<div class="gfi-section">
        <div class="gfi-title">${label}</div>
        <table class="gfi-table">${rows}</table>
      </div>`
    })
    .join('<hr class="gfi-hr">')

  return `<div class="gfi-popup">${sections}</div>`
}

// ── Hover — cursor + highlight ────────────────────────────────────────────────

function handleMouseMove(e) {
  if (getInfoActiveLayers().length === 0) {
    map.getContainer().style.cursor = 'default'
    clearHighlight()
    return
  }
  clearTimeout(mouseMoveTimeout)
  mouseMoveTimeout = setTimeout(() => checkHover(e.latlng), 120)
}

async function checkHover(latlng) {
  const layers = getInfoActiveLayers()
  if (layers.length === 0) return

  hoverAbortController?.abort()
  hoverAbortController = new AbortController()

  try {
    // Consulta apenas a primeira camada ativa para desempenho no hover
    const feature = await fetchGFI(layers[0], latlng, hoverAbortController.signal)
    if (feature) {
      map.getContainer().style.cursor = 'pointer'
      highlightFeature(feature)
    } else {
      map.getContainer().style.cursor = 'crosshair'
      clearHighlight()
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      map.getContainer().style.cursor = 'default'
      clearHighlight()
    }
  }
}

function handleMouseOut() {
  clearTimeout(mouseMoveTimeout)
  hoverAbortController?.abort()
  map.getContainer().style.cursor = 'default'
  clearHighlight()
}

function highlightFeature(feature) {
  clearHighlight()
  const { type, coordinates } = feature.geometry ?? {}
  if (!coordinates) return

  let latlngs = null
  if (type === 'Polygon') {
    latlngs = coordinates[0].map(([lng, lat]) => [lat, lng])
  } else if (type === 'MultiPolygon') {
    // Desenha todos os anéis do MultiPolygon
    latlngs = coordinates.map((poly) => poly[0].map(([lng, lat]) => [lat, lng]))
  }

  if (!latlngs) return

  highlightLayer = L.polygon(latlngs, {
    color: '#00d4aa',
    weight: 2,
    opacity: 0.9,
    fillColor: '#00d4aa',
    fillOpacity: 0.12,
    dashArray: '5,4',
  }).addTo(map)
}

function clearHighlight() {
  if (highlightLayer) {
    map.removeLayer(highlightLayer)
    highlightLayer = null
  }
}

// Ao desligar o modo info em todas as camadas, limpa estado visual
watch(
  () => mapStore.infoActive,
  (active) => {
    if (!map) return
    const hasAny = Object.values(active).some(Boolean)
    if (!hasAny) {
      clearHighlight()
      map.getContainer().style.cursor = 'default'
    }
  },
  { deep: true },
)
</script>

<template>
  <div ref="mapEl" class="map-container" />
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
