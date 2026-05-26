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

const paraibaBounds = [
  [-8.3, -38.76],
  [-6.02, -35.17]
]

// Cache de memória para reuso dos buffers binários PBF
const tileDataCache = new Map()

onMounted(async () => {
  await nextTick()

  if (!mapEl.value) {
    console.warn('⚠️ Contêiner do mapa não foi encontrado no DOM ainda.')
    return
  }

  map = L.map(mapEl.value, { zoomControl: false }).fitBounds(paraibaBounds)

  // Bounds com padding generoso para o popup não ser cortado nas bordas
  const BOUNDS_PADDING = 1.5 // graus de margem extra ao redor da área de interesse
  const [[swLat, swLng], [neLat, neLng]] = paraibaBounds
  const maxBounds = L.latLngBounds(
    L.latLng(swLat - BOUNDS_PADDING, swLng - BOUNDS_PADDING),
    L.latLng(neLat + BOUNDS_PADDING, neLng + BOUNDS_PADDING)
  )

  map.setMaxBounds(maxBounds)
  map.setMinZoom(7)           // impede zoom out demais
  map.options.maxBoundsViscosity = 1.0  // torna os bounds rígidos (sem elástico)


  // Controle de zoom + home unificado
const ZoomHomeControl = L.Control.extend({
  onAdd(map) {
    const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control zoom-home-control')

    // Botão zoom +
    const zoomIn = L.DomUtil.create('button', 'zoom-btn', container)
    zoomIn.innerHTML = '<i class="bi bi-plus"></i>'
    zoomIn.title = 'Aproximar'
    L.DomEvent.on(zoomIn, 'click', (e) => {
      L.DomEvent.stopPropagation(e)
      map.zoomIn()
    })

    // Botão home
    const home = L.DomUtil.create('button', 'zoom-btn home-btn', container)
    home.innerHTML = '<i class="bi bi-fullscreen"></i>'
    home.title = 'Voltar à visão inicial'
    L.DomEvent.on(home, 'click', (e) => {
      L.DomEvent.stopPropagation(e)
      map.fitBounds(paraibaBounds)
    })

    // Botão zoom -
    const zoomOut = L.DomUtil.create('button', 'zoom-btn', container)
    zoomOut.innerHTML = '<i class="bi bi-dash"></i>'
    zoomOut.title = 'Afastar'
    L.DomEvent.on(zoomOut, 'click', (e) => {
      L.DomEvent.stopPropagation(e)
      map.zoomOut()
    })

    return container
  }
})
new ZoomHomeControl({ position: 'topleft' }).addTo(map)

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

          const targetY = coords.y


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
    try {
      const cacheKey = `${coords.z}-${coords.x}-${targetY}-${sourceLayer}`
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
    } catch(e) {
      console.error('[Decode Error]', e)
      done(null, tile)
    }
  })
  .catch((err) => {
    console.error(`[Fetch Error] ${tileUrl}:`, err)
    done(null, tile)
  })

          return tile
        }
      })

      const layer = new CustomMVTLayer({
        minZoom: 2,
        maxZoom: 14,
        zIndex: zIndex,
        bounds: paraibaBounds
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
  
  const targetY = layerPoint.y

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

/* ── Controle de zoom customizado ────────────────────────────────────────────── */
:deep(.zoom-home-control) {
  display: flex;
  flex-direction: column;
  border: none !important;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

:deep(.zoom-btn) {
  width: 34px;
  height: 34px;
  border: none;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 700;
  transition: background 0.15s, color 0.15s;
}

:deep(.zoom-btn:last-child) {
  border-bottom: none;
}

:deep(.zoom-btn:hover) {
  background: var(--bg-card-hover);
  color: var(--accent);
}

:deep(.home-btn) {
  font-size: 0.9rem;
  color: var(--text-dim);
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

:deep(.home-btn:hover) {
  color: var(--accent);
}
</style>