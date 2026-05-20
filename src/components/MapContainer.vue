<template>
  <div ref="mapEl" class="map-container" />
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { VectorTile } from 'vector-tile'
import Pbf from 'pbf'

// Utilitários isolados
import { getThematicColor, drawGeometryToContext } from '@/utils/mapRenderer'
import { createPopupContent } from '@/utils/mapPopup'

const mapStore = useMapStore()
const mapEl = ref(null)

let map = null
let currentTileLayer = null
const activeOverlays = new Map() 

// Cache de memória para reuso dos buffers binários PBF
const tileDataCache = new Map()

onMounted(async () => {
  await nextTick()

  if (!mapEl.value) {
    console.warn('⚠️ Contêiner do mapa não foi encontrado no DOM ainda.')
    return
  }

  const paraibaBounds = [
    [-8.300000000000000, -38.7599999999999980],
    [-6.0200000000000005, -35.1700000000000017]
  ]

  map = L.map(mapEl.value).fitBounds(paraibaBounds)
  renderTileLayer()
  syncVectorOverlays(mapStore.visibleOverlays)

  // ── Ouvinte de Clique Global do Mapa ──
  map.on('click', handleMapClick)
})

onUnmounted(() => {
  if (map) {
    map.off('click', handleMapClick)
    map.remove()
    map = null
  }
  tileDataCache.clear()
})

// ── 1. Gerenciamento do Mapa de Fundo ──────────────────────────────────────────
watch(() => mapStore.activeBaseLayer, renderTileLayer)

function renderTileLayer() {
  const { url, label, meta, active, ...leafletOptions } = mapStore.activeBaseLayer
  const opacity = mapStore.layerOpacity[mapStore.activeBaseLayerKey] ?? 1
  if (currentTileLayer) map.removeLayer(currentTileLayer)
  currentTileLayer = L.tileLayer(url, { ...leafletOptions, opacity, zIndex: 1 }).addTo(map)
}

// ── 2. Sincronização Dinâmica das Camadas Vetoriais (MVT Nativo) ───────────────
watch(
  () => mapStore.visibleOverlays,
  (desired) => { if (map) syncVectorOverlays(desired) },
  { deep: true },
)

function syncVectorOverlays(desired) {
  for (const { key, url, sourceLayer, zIndex } of mapStore.availableOverlays) {
    const shouldBeVisible = desired[key]
    const isOnMap         = activeOverlays.has(key)

    if (shouldBeVisible && !isOnMap) {
      const CustomMVTLayer = L.GridLayer.extend({
        createTile: function (coords, done) {
          const tile = document.createElement('canvas')
          const size = this.getTileSize()
          tile.width = size.x
          tile.height = size.y
          const ctx = tile.getContext('2d')

          const tileUrl = url
            .replace('{z}', coords.z)
            .replace('{x}', coords.x)
            .replace('{y}', coords.y)

          fetch(tileUrl)
            .then(res => {
              if (!res.ok) throw new Error('Tile pbf não encontrado')
              return res.arrayBuffer()
            })
            .then(buffer => {
              const cacheKey = `${coords.z}-${coords.x}-${coords.y}-${sourceLayer}`
              tileDataCache.set(cacheKey, buffer)

              const pbf = new Pbf(new Uint8Array(buffer))
              const vt = new VectorTile(pbf)
              const layer = vt.layers[sourceLayer]
              
              if (!layer) {
                done(null, tile)
                return
              }

              const currentOpacity = mapStore.layerOpacity[key] ?? 1

              for (let i = 0; i < layer.length; i++) {
                const feature = layer.feature(i)
                const geom = feature.loadGeometry()
                const props = feature.properties
                const color = getThematicColor(sourceLayer, props)

                drawGeometryToContext(ctx, geom, feature.type, size)

                ctx.fillStyle = color
                ctx.globalAlpha = 0.8 * currentOpacity
                ctx.fill()
              }
              done(null, tile)
            })
            .catch(() => {
              done(null, tile)
            })

          return tile
        }
      })

      const layer = new CustomMVTLayer({
        minZoom: 2,
        maxZoom: 14,
        zIndex: zIndex
      }).addTo(map)

      activeOverlays.set(key, layer)

    } else if (!shouldBeVisible && isOnMap) {
      map.removeLayer(activeOverlays.get(key))
      activeOverlays.delete(key)
      
      // Limpa registros antigos de cache daquela camada para liberar memória
      for (const cacheKey of tileDataCache.keys()) {
        if (cacheKey.endsWith(`-${sourceLayer}`)) {
          tileDataCache.delete(cacheKey)
        }
      }
    }
  }
}

// ── 3. Identificação Unificada Multicamadas (Multi-GetFeatureInfo Local) ───────
async function handleMapClick(e) {
  const zoom = map.getZoom()
  const layerPoint = map.project(e.latlng, zoom).divideBy(256).floor()
  
  const layersToQuery = mapStore.availableOverlays.filter(layer => mapStore.visibleOverlays[layer.key])
  
  if (layersToQuery.length === 0) return

  const popupPromises = layersToQuery.map(async (overlay) => {
    const { key, url, sourceLayer, label } = overlay
    const cacheKey = `${zoom}-${layerPoint.x}-${layerPoint.y}-${sourceLayer}`

    // Helper interno para extrair propriedades do primeiro feature encontrado no quadrante
    const parseProperties = (buffer) => {
      const pbf = new Pbf(new Uint8Array(buffer))
      const vt = new VectorTile(pbf)
      const layer = vt.layers[sourceLayer]
      if (layer && layer.length > 0) {
        return { label, properties: layer.feature(0).properties }
      }
      return null
    }

    // Se estiver no cache, resolve imediatamente
    if (tileDataCache.has(cacheKey)) {
      return parseProperties(tileDataCache.get(cacheKey))
    }

    // Fallback remoto caso o quadrante ainda não tenha cacheado (ex: transição rápida de zoom)
    try {
      const tileUrl = url
        .replace('{z}', zoom)
        .replace('{x}', layerPoint.x)
        .replace('{y}', layerPoint.y)
      
      const res = await fetch(tileUrl)
      if (!res.ok) return null
      const buffer = await res.arrayBuffer()
      
      // Atualiza o cache para cliques futuros no mesmo lugar
      tileDataCache.set(cacheKey, buffer)
      return parseProperties(buffer)
    } catch {
      return null
    }
  })

  // Aguarda a resolução dos buffers de todas as camadas ativas simultaneamente
  const results = await Promise.all(popupPromises)
  const validLayersData = results.filter(item => item !== null)

  if (validLayersData.length > 0) {
    const htmlContent = createPopupContent(validLayersData)
    
    L.popup({ className: 'popup-dark', maxWidth: 350 })
      .setLatLng(e.latlng)
      .setContent(htmlContent)
      .openOn(map)
  }
}

// ── 4. Controle Suave de Opacidade ───────────────────────────────────────────
let redrawTimeout = null
watch(
  () => mapStore.layerOpacity,
  (opacities) => {
    const baseKey = mapStore.activeBaseLayerKey
    if (currentTileLayer && baseKey in opacities) {
      currentTileLayer.setOpacity(opacities[baseKey])
    }
    
    clearTimeout(redrawTimeout)
    redrawTimeout = setTimeout(() => {
      activeOverlays.forEach((layer) => layer.redraw())
    }, 50)
  },
  { deep: true },
)
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}

/* Customização Estilizada dos Popups */
:deep(.popup-dark .leaflet-popup-content-wrapper) {
  background: #111827;
  color: #f3f4f6;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  border: 1px solid #374151;
  max-height: 400px;
  overflow-y: auto; /* Garante scroll caso muitas camadas fiquem ativas */
}
:deep(.popup-dark .leaflet-popup-tip) {
  background: #111827;
}
:deep(.gfi-title) {
  font-weight: bold;
  font-size: 0.9rem;
  color: #38bdf8;
  border-bottom: 1px solid #374151;
  padding-bottom: 6px;
  margin-bottom: 8px;
}
:deep(.gfi-table) {
  width: 100%;
  font-size: 0.75rem;
  border-collapse: collapse;
}
:deep(.gfi-table tr:nth-child(even)) {
  background: rgba(255, 255, 255, 0.03);
}
:deep(.gfi-key) {
  font-weight: 600;
  color: #34d399;
  padding: 4px 8px 4px 0;
  vertical-align: top;
  text-transform: capitalize;
}
:deep(.gfi-val) {
  color: #e5e7eb;
  padding: 4px 0;
  word-break: break-word;
}
</style>