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

// ── 2. Sincronização Dinâmica das Camadas Vetoriais (MVT Híbrido: XYZ local / TMS prod) ──
watch(
  (() => mapStore.visibleOverlays),
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

          // 🌟 CONDICIONAL DE AMBIENTE PARA A URL:
          // Se for DEV (local), mantém coords.y direto.
          // Se for PROD (Tomcat remoto), calcula o Y invertido do padrão TMS.
          const targetY = import.meta.env.DEV 
            ? coords.y 
            : Math.pow(2, coords.z) - 1 - coords.y

          const tileUrl = url
            .replace('{z}', coords.z)
            .replace('{x}', coords.x)
            .replace('{y}', targetY)

          fetch(tileUrl)
            .then(res => {
              if (!res.ok) throw new Error(`Tile PBF não encontrado na URL: ${tileUrl}`)
              return res.arrayBuffer()
            })
            .then(buffer => {
              // Cache amarrado ao targetY do ambiente para consistência no clique posterior
              const cacheKey = `${coords.z}-${coords.x}-${targetY}-${sourceLayer}`
              tileDataCache.set(cacheKey, buffer)

              const pbf = new Pbf(new Uint8Array(buffer))
              const vt = new VectorTile(pbf)
              const layer = vt.layers[sourceLayer]
              
              if (!layer) {
                console.error(`❌ [MVT Error] A camada interna "${sourceLayer}" não existe dentro do arquivo PBF carregado de: ${tileUrl}. Camadas disponíveis no arquivo:`, Object.keys(vt.layers))
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
            .catch((err) => {
              console.warn(`[GridLayer Warning] Falha ao processar bloco MVT:`, err.message)
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
      
      for (const cacheKey of tileDataCache.keys()) {
        if (cacheKey.endsWith(`-${sourceLayer}`)) {
          tileDataCache.delete(cacheKey)
        }
      }
    }
  }
}

// ── 3. Identificação Unificada Multicamadas (Corrigida) ───────
async function handleMapClick(e) {
  const zoom = map.getZoom()
  const point = map.project(e.latlng, zoom)
  const layerPoint = point.divideBy(256).floor()
  
  // Coordenadas locais dentro do tile (0-4096) para precisão no clique
  const clickX = (point.x % 256) * (4096 / 256)
  const clickY = (point.y % 256) * (4096 / 256)
  
  const targetY = import.meta.env.DEV
    ? layerPoint.y
    : Math.pow(2, zoom) - 1 - layerPoint.y

  const layersToQuery = mapStore.availableOverlays.filter(layer => mapStore.visibleOverlays[layer.key])
  if (layersToQuery.length === 0) return

  const popupPromises = layersToQuery.map(async (overlay) => {
    const { key, url, sourceLayer, label } = overlay
    const cacheKey = `${zoom}-${layerPoint.x}-${targetY}-${sourceLayer}`

    const parseProperties = (buffer) => {
      try {
        // Validação básica: se o buffer for muito pequeno ou começar com '<' (HTML), ignore
        const uint8 = new Uint8Array(buffer)
        if (uint8.length < 10 || uint8[0] === 0x3C) return null 

        const pbf = new Pbf(uint8)
        const vt = new VectorTile(pbf)
        const layer = vt.layers[sourceLayer]
        
        if (layer && layer.length > 0) {
          // Itera pelas feições para ver qual delas contém o ponto do clique
          for (let i = 0; i < layer.length; i++) {
            const feature = layer.feature(i)
            const bbox = feature.bbox() // [x1, y1, x2, y2]
            
            // Verifica se o clique está dentro do bounding box da geometria
            if (clickX >= bbox[0] && clickX <= bbox[2] && 
                clickY >= bbox[1] && clickY <= bbox[3]) {
              return { label, properties: feature.properties }
            }
          }
        }
      } catch (err) {
        console.warn(`[MVT Parse Error] Erro ao processar tile para ${label}:`, err.message)
      }
      return null
    }

    if (tileDataCache.has(cacheKey)) {
      return parseProperties(tileDataCache.get(cacheKey))
    }

    try {
      const tileUrl = url
        .replace('{z}', zoom)
        .replace('{x}', layerPoint.x)
        .replace('{y}', targetY)
      
      const res = await fetch(tileUrl)
      if (!res.ok) return null
      
      // Verifica se o conteúdo é realmente um binário/pbf
      const contentType = res.headers.get('content-type')
      if (contentType && contentType.includes('text/html')) return null

      const buffer = await res.arrayBuffer()
      tileDataCache.set(cacheKey, buffer)
      return parseProperties(buffer)
    } catch {
      return null
    }
  })

  const results = await Promise.all(popupPromises)
  const validLayersData = results.filter(item => item !== null)

  if (validLayersData.length > 0) {
    const htmlContent = createPopupContent(validLayersData)
    L.popup({ className: 'popup-dark', maxWidth: 350 })
      .setLatLng(e.latlng)
      .setContent(htmlContent)
      .openOn(map)
  } else {
    // Se não houver dados válidos, garante que qualquer popup aberto seja fechado
    map.closePopup()
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

:deep(.popup-dark .leaflet-popup-content-wrapper) {
  background: #111827;
  color: #f3f4f6;
  border-radius: 6px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  border: 1px solid #374151;
  max-width: 250px !important; 
  max-height: 280px;
  overflow-y: auto;
}

:deep(.popup-dark .leaflet-popup-content) {
  margin: 10px 12px;
  line-height: 1.4;
}

:deep(.popup-dark .leaflet-popup-tip) {
  background: #111827;
  border: 1px solid #374151;
  box-shadow: none;
}

:deep(.popup-dark .leaflet-popup-close-button) {
  color: #9ca3af !important;
  padding: 6px 4px 0 0 !important;
}

:deep(.popup-dark .leaflet-popup-close-button:hover) {
  color: #f3f4f6 !important;
  background: transparent !important;
}

:deep(.gfi-section) {
  border-bottom: 1px dashed #374151;
  padding-bottom: 8px;
  margin-bottom: 8px;
}

:deep(.gfi-section:last-of-type) {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

:deep(.gfi-title) {
  font-weight: 700;
  font-size: 0.75rem;
  color: #38bdf8;
  margin-top: 2px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.gfi-table) {
  width: 100%;
  font-size: 0.72rem;
  border-collapse: collapse;
}

:deep(.gfi-table tr:nth-child(even)) {
  background: rgba(255, 255, 255, 0.03);
}

:deep(.gfi-key) {
  font-weight: 600;
  color: #34d399;
  padding: 3px 6px 3px 0;
  vertical-align: top;
  text-transform: capitalize;
  width: 45%;
}

:deep(.gfi-val) {
  color: #e5e7eb;
  padding: 3px 0;
  vertical-align: top;
  word-break: break-word;
}

:deep(.gfi-empty) {
  font-size: 0.72rem;
  color: #9ca3af;
  padding: 3px 0;
  font-style: italic;
}
</style>