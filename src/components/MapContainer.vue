<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useMapStore, WMS_URL } from '@/stores/mapStore'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapStore = useMapStore()

// Referência ao elemento DOM onde o Leaflet será montado
const mapEl = ref(null)

// Instâncias do Leaflet fora do sistema reativo do Vue
let map = null
let currentTileLayer = null

// Mapa de instâncias WMS ativas: chave da camada → L.TileLayer.WMS
const wmsLayers = new Map()

onMounted(() => {
  // Extensão do Semiárido: [SW, NE] no formato [[lat, lng], [lat, lng]]
  const semiaridoBounds = [
    [-17.9954314609998995, -46.5772829000000002],
    [-2.6851430819999700, -35.2625510709999972],
  ]

  map = L.map(mapEl.value).fitBounds(semiaridoBounds)
  renderTileLayer()
  syncOverlays(mapStore.visibleOverlays)
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

// ── Camada Base ───────────────────────────────────────────────────────────────

watch(() => mapStore.activeBaseLayer, renderTileLayer)

function renderTileLayer() {
  const { url, attribution, maxZoom } = mapStore.activeBaseLayer
  if (currentTileLayer) map.removeLayer(currentTileLayer)
  currentTileLayer = L.tileLayer(url, { attribution, maxZoom }).addTo(map)
}

// ── Camadas de Sobreposição (WMS) ─────────────────────────────────────────────

// Observa o objeto inteiro de visibilidade (deep) para reagir a qualquer toggle
watch(
  () => mapStore.visibleOverlays,
  (desired) => {
    if (!map) return
    syncOverlays(desired)
  },
  { deep: true },
)

/**
 * Reconcilia o estado desejado (store) com as camadas WMS efetivamente no mapa.
 * Adiciona camadas que devem aparecer e remove as que foram desligadas.
 */
function syncOverlays(desired) {
  for (const { key, wmsLayer } of mapStore.availableOverlays) {
    const shouldBeVisible = desired[key]
    const isOnMap = wmsLayers.has(key)

    if (shouldBeVisible && !isOnMap) {
      const layer = L.tileLayer
        .wms(WMS_URL, {
          layers: wmsLayer,
          format: 'image/png',
          transparent: true,
          // Garante que o WMS fique acima da camada base
          zIndex: 10,
          attribution: 'INSA / GeoServer',
        })
        .addTo(map)

      wmsLayers.set(key, layer)
    } else if (!shouldBeVisible && isOnMap) {
      map.removeLayer(wmsLayers.get(key))
      wmsLayers.delete(key)
    }
  }
}
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
