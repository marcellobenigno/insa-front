<template>
  <div class="map-shell">
    <div ref="mapEl" class="map-container" />
    <WebGisTour />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useSidebar } from '@/composables/useSidebar'
import WebGisTour from './WebGisTour.vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { VectorTile } from 'vector-tile'
import Pbf from 'pbf'

// Utilitários isolados
import { getThematicColor, drawGeometryToContext, parseColor, matchesFilter } from '@/utils/mapRenderer'
import { createPopupContent } from '@/utils/mapPopup'

const mapStore = useMapStore()
const { isCollapsed, toggleSidebar } = useSidebar()
const mapEl = ref(null)

let map = null
let currentTileLayer = null
let searchMarker = null
let fullscreenChangeHandler = null
const activeOverlays = new Map()

// Estado de medição nativa
let measureMode = false
let measureClosed = false
let measurePoints = []
let measurePolyline = null
let measureDotLayers = []
let measureTooltip = null
let measureBtnRef = null

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


  // Controle unificado: Fullscreen + Locate + Zoom + Home
  const ZoomHomeControl = L.Control.extend({
    onAdd(map) {
      const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control zoom-home-control')

      // ── 1. Zoom In ──────────────────────────────────────────────────────────────
      const zoomIn = L.DomUtil.create('button', 'zoom-btn', container)
      zoomIn.innerHTML = '<i class="bi bi-plus"></i>'
      zoomIn.title = 'Aproximar'
      L.DomEvent.on(zoomIn, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.zoomIn()
      })

      // ── 2. Home ─────────────────────────────────────────────────────────────────
      const home = L.DomUtil.create('button', 'zoom-btn home-btn', container)
      home.innerHTML = '<i class="bi bi-house"></i>'
      home.title = 'Voltar à visão inicial'
      L.DomEvent.on(home, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.fitBounds(paraibaBounds)
      })

      // ── 3. Zoom Out ─────────────────────────────────────────────────────────────
      const zoomOut = L.DomUtil.create('button', 'zoom-btn', container)
      zoomOut.innerHTML = '<i class="bi bi-dash"></i>'
      zoomOut.title = 'Afastar'
      L.DomEvent.on(zoomOut, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        map.zoomOut()
      })

      // ── 4. Tela cheia (oculto em mobile — fullscreen API não suportada) ──────────
      if (document.fullscreenEnabled) {
        const fsBtn = L.DomUtil.create('button', 'zoom-btn', container)
        fsBtn.innerHTML = '<i class="bi bi-arrows-angle-expand"></i>'
        fsBtn.title = 'Tela cheia'

        let sidebarWasExpanded = false

        fullscreenChangeHandler = () => {
          if (!document.fullscreenElement) {
            fsBtn.innerHTML = '<i class="bi bi-arrows-angle-expand"></i>'
            fsBtn.title = 'Tela cheia'
            fsBtn.classList.remove('is-active')
            if (sidebarWasExpanded) {
              toggleSidebar()
              sidebarWasExpanded = false
            }
          }
        }
        document.addEventListener('fullscreenchange', fullscreenChangeHandler)

        L.DomEvent.on(fsBtn, 'click', (e) => {
          L.DomEvent.stopPropagation(e)
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen?.()
            fsBtn.innerHTML = '<i class="bi bi-arrows-angle-contract"></i>'
            fsBtn.title = 'Sair da tela cheia'
            fsBtn.classList.add('is-active')
            if (!isCollapsed.value) {
              sidebarWasExpanded = true
              toggleSidebar()
            }
          } else {
            document.exitFullscreen?.()
          }
        })
      }

      // ── 5. Localização GPS ──────────────────────────────────────────────────────
      let locMarker = null
      let locCircle = null
      const locBtn = L.DomUtil.create('button', 'zoom-btn', container)
      locBtn.innerHTML = '<i class="bi bi-crosshair"></i>'
      locBtn.title = 'Minha localização'

      L.DomEvent.on(locBtn, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        if (locMarker) {
          map.removeLayer(locMarker)
          if (locCircle) map.removeLayer(locCircle)
          locMarker = null
          locCircle = null
          locBtn.innerHTML = '<i class="bi bi-crosshair"></i>'
          locBtn.title = 'Minha localização'
          locBtn.classList.remove('is-active')
          return
        }
        if (!navigator.geolocation) {
          locBtn.title = 'Geolocalização não suportada'
          return
        }
        locBtn.innerHTML = '<i class="bi bi-arrow-repeat loc-spinner"></i>'
        locBtn.title = 'Localizando…'

        navigator.geolocation.getCurrentPosition(
          ({ coords: { latitude: lat, longitude: lng, accuracy } }) => {
            locBtn.innerHTML = '<i class="bi bi-crosshair2"></i>'
            locBtn.title = 'Remover localização'
            locBtn.classList.add('is-active')

            locMarker = L.circleMarker([lat, lng], {
              radius: 8, fillColor: 'var(--accent)',
              color: '#fff', weight: 2.5, fillOpacity: 1,
            }).addTo(map)

            locCircle = L.circle([lat, lng], {
              radius: accuracy, color: 'var(--accent)',
              fillColor: 'var(--accent)', fillOpacity: 0.1, weight: 1,
            }).addTo(map)

            map.flyTo([lat, lng], 13, { duration: 1 })
          },
          (err) => {
            locBtn.innerHTML = '<i class="bi bi-crosshair"></i>'
            locBtn.title = 'Localização não disponível'
            console.warn('[Locate]', err.message)
          },
          { enableHighAccuracy: true, timeout: 10000 },
        )
      })

      // ── 6. Medição ──────────────────────────────────────────────────────────────
      const measBtn = L.DomUtil.create('button', 'zoom-btn', container)
      measBtn.innerHTML = '<i class="bi bi-rulers"></i>'
      measBtn.title = 'Medir distância / área'
      measureBtnRef = measBtn

      L.DomEvent.on(measBtn, 'click', (e) => {
        L.DomEvent.stopPropagation(e)
        if (measureMode || measurePoints.length > 0) {
          clearMeasure()
        } else {
          measureMode = true
          measBtn.classList.add('is-active')
          measBtn.title = 'Cancelar medição'
          map.getContainer().style.cursor = 'crosshair'
        }
      })

      return container
    },
  })
  new ZoomHomeControl({ position: 'topleft' }).addTo(map)

  // Barra de escala (nativo Leaflet)
  L.control.scale({ imperial: false, position: 'bottomright' }).addTo(map)

  renderTileLayer()
  syncVectorOverlays(mapStore.visibleOverlays)

  // ── Ouvinte de Clique Global do Mapa ──
  map.on('click', handleMapClick)

  // ── Coordenadas do cursor em tempo real ──
  map.on('mousemove', (e) => mapStore.setMouseCoords({ lat: e.latlng.lat, lng: e.latlng.lng }))
})

onUnmounted(() => {
  clearMeasure()
  if (fullscreenChangeHandler) {
    document.removeEventListener('fullscreenchange', fullscreenChangeHandler)
    fullscreenChangeHandler = null
  }
  if (map) {
    map.off('click', handleMapClick)
    map.remove()
    map = null
  }
  tileDataCache.clear()
})

// ── Ícone personalizado para marcador de busca ─────────────────────────────────
function makeSearchIcon() {
  return L.divIcon({
    className: '',
    html: `<div class="search-marker-icon"><i class="bi bi-geo-alt-fill"></i></div>`,
    iconSize:   [28, 36],
    iconAnchor: [14, 36],
    popupAnchor:[0, -36],
  })
}

// ── Medição nativa ────────────────────────────────────────────────────────────
function formatDist(m) {
  return m >= 1000 ? `${(m / 1000).toFixed(2)} km` : `${Math.round(m)} m`
}

function formatArea(m2) {
  if (m2 >= 1_000_000) return `${(m2 / 1_000_000).toFixed(2)} km²`
  if (m2 >= 10_000)    return `${(m2 / 10_000).toFixed(2)} ha`
  return `${Math.round(m2)} m²`
}

function calcTotalDist() {
  let d = 0
  for (let i = 1; i < measurePoints.length; i++)
    d += measurePoints[i - 1].distanceTo(measurePoints[i])
  return d
}

function calcArea() {
  // Exclui o ponto de fechamento (repetido) antes de calcular
  const pts = measureClosed ? measurePoints.slice(0, -1) : measurePoints
  const n = pts.length
  if (n < 3) return 0
  const toRad = Math.PI / 180
  const R = 6_371_000
  const lat0 = pts[0].lat * toRad
  let area = 0
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n
    area += pts[i].lng * pts[j].lat
    area -= pts[j].lng * pts[i].lat
  }
  return Math.abs(area / 2) * toRad * toRad * R * R * Math.cos(lat0)
}

function updateMeasureTooltip() {
  if (measureTooltip) map.removeLayer(measureTooltip)
  if (measurePoints.length < 2) return
  const last = measurePoints[measurePoints.length - 1]
  const dist = calcTotalDist()
  const area = calcArea()
  const html = `<div class="meas-tip">
    <span>📏 ${formatDist(dist)}</span>
    ${measureClosed && area > 0 ? `<span>📐 ${formatArea(area)}</span>` : ''}
  </div>`
  measureTooltip = L.tooltip({ permanent: true, direction: 'right', className: 'meas-tooltip', offset: [10, 0] })
    .setLatLng(last).setContent(html).addTo(map)
}

function clearMeasure() {
  measureMode = false
  measureClosed = false
  measurePoints = []
  if (measurePolyline) { map?.removeLayer(measurePolyline); measurePolyline = null }
  measureDotLayers.forEach(l => map?.removeLayer(l))
  measureDotLayers = []
  if (measureTooltip) { map?.removeLayer(measureTooltip); measureTooltip = null }
  if (measureBtnRef) {
    measureBtnRef.classList.remove('is-active')
    measureBtnRef.title = 'Medir distância / área'
    measureBtnRef.innerHTML = '<i class="bi bi-rulers"></i>'
  }
  if (map) map.getContainer().style.cursor = ''
}

function addMeasurePoint(latlng) {
  // Detecta fechamento: clique dentro de 15px do primeiro ponto (≥ 3 pontos)
  if (measurePoints.length >= 3) {
    const firstPx = map.latLngToContainerPoint(measurePoints[0])
    const clickPx = map.latLngToContainerPoint(latlng)
    if (firstPx.distanceTo(clickPx) <= 15) {
      measurePoints.push(measurePoints[0]) // fecha o polígono
      measureClosed = true
      measureMode = false
      map.getContainer().style.cursor = ''
      if (measureBtnRef) {
        measureBtnRef.classList.remove('is-active')
        measureBtnRef.title = 'Limpar medição'
      }
      // Redesenha como linha sólida fechada
      if (measurePolyline) map.removeLayer(measurePolyline)
      measurePolyline = L.polyline(measurePoints, {
        color: 'var(--accent)', weight: 2,
      }).addTo(map)
      updateMeasureTooltip()
      return
    }
  }

  measurePoints.push(latlng)

  const dot = L.circleMarker(latlng, {
    radius: 4, fillColor: 'var(--accent)', color: '#fff', weight: 2, fillOpacity: 1,
  }).addTo(map)
  measureDotLayers.push(dot)

  if (measurePolyline) map.removeLayer(measurePolyline)
  if (measurePoints.length > 1) {
    measurePolyline = L.polyline(measurePoints, {
      color: 'var(--accent)', weight: 2, dashArray: '6 4',
    }).addTo(map)
  }
  updateMeasureTooltip()
}

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
      const activeFilter   = mapStore.layerSearchFilters?.[key] ?? null
      let anyMatch = false
      for (let i = 0; i < layer.length; i++) {
        try {
          const feature = layer.feature(i)
          const geom = feature.loadGeometry()
          const props = feature.properties
          const rawColor = getThematicColor(sourceLayer, props)
          const { strokeOnly, color } = parseColor(rawColor)
          const isMatch = !activeFilter || matchesFilter(props, activeFilter)
          if (activeFilter && isMatch) anyMatch = true

          drawGeometryToContext(ctx, geom, feature.type, size)

          if (strokeOnly) {
            // Camada de contorno (ex: municípios)
            if (activeFilter && !isMatch) {
              ctx.strokeStyle = '#6b7280'
              ctx.lineWidth   = 1
              ctx.globalAlpha = 0.15 * currentOpacity
            } else {
              const baseWidth =
                sourceLayer === 'limite_semiarido_pb' || sourceLayer === 'limite_do_semiarido_br'
                  ? 3
                  : 1.5
              ctx.strokeStyle = color
              ctx.lineWidth   = activeFilter && isMatch ? baseWidth + 1 : baseWidth
              ctx.globalAlpha = 0.9 * currentOpacity
            }
            ctx.stroke()
          } else {
            // Camada de preenchimento
            if (activeFilter && !isMatch) {
              ctx.fillStyle   = '#6b7280'
              ctx.globalAlpha = 0.12 * currentOpacity
              ctx.fill()
            } else {
              ctx.fillStyle   = color
              ctx.globalAlpha = 0.8 * currentOpacity
              ctx.fill()
              // Borda de destaque amarela nas feições que batem com o filtro
              if (activeFilter && isMatch) {
                ctx.strokeStyle = '#fbbf24'
                ctx.lineWidth   = 2
                ctx.globalAlpha = currentOpacity
                ctx.stroke()
              }
            }
          }
        } catch {
          // Ignora feições com tipo de geometria não suportado (ex: type 4)
        }
      }
      if (activeFilter && anyMatch && mapStore.layerSearchMatchCounts?.[key] === 0) {
        mapStore.setSearchMatchCount(key, 1)
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
  if (measureMode) { addMeasurePoint(e.latlng); return }

  const zoom = map.getZoom()
  const point = map.project(e.latlng, zoom)
  const layerPoint = point.divideBy(256).floor()
  
  // Coordenadas locais dentro do tile (0-4096) para precisão no clique
  const clickX = (point.x % 256) * (4096 / 256)
  const clickY = (point.y % 256) * (4096 / 256)
  
  const targetY = layerPoint.y

  const layersToQuery = mapStore.availableOverlays.filter(layer => mapStore.visibleOverlays[layer.key] && !layer.noPopup)
  if (layersToQuery.length === 0) return

  const popupPromises = layersToQuery.map(async (overlay) => {
    const { key, url, sourceLayer, label, popUpFields, descFields } = overlay
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
              return { label, properties: feature.properties, popUpFields, descFields }
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


// ── 4. Redesenho ao mudar filtro de busca ────────────────────────────────────

function countFilterMatches(key) {
  const overlay = mapStore.availableOverlays.find(o => o.key === key)
  if (!overlay) return
  const filter = mapStore.layerSearchFilters[key]
  if (!filter) { mapStore.setSearchMatchCount(key, null); return }

  const { sourceLayer } = overlay
  let found = false

  for (const [cacheKey, buffer] of tileDataCache.entries()) {
    if (!cacheKey.endsWith(`-${sourceLayer}`)) continue
    try {
      const pbf = new Pbf(new Uint8Array(buffer))
      const vt = new VectorTile(pbf)
      const layer = vt.layers[sourceLayer]
      if (!layer) continue
      for (let i = 0; i < layer.length; i++) {
        if (matchesFilter(layer.feature(i).properties, filter)) {
          found = true
          break
        }
      }
    } catch { /* ignora tiles corrompidos */ }
    if (found) break
  }

  mapStore.setSearchMatchCount(key, found ? 1 : 0)
}

watch(
  () => mapStore.layerSearchFilters,
  (filters) => {
    if (!map) return
    for (const [key, filter] of Object.entries(filters)) {
      if (activeOverlays.has(key)) {
        activeOverlays.get(key).redraw()
      }
      if (filter && !mapStore.visibleOverlays[key]) {
        mapStore.toggleOverlay(key)
      }
      countFilterMatches(key)
    }
  },
  { deep: true },
)

// ── 5. Controle Suave de Opacidade ───────────────────────────────────────────
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

// ── 6. Redimensionamento ao colapsar/expandir a sidebar ───────────────────────
// A sidebar anima por --transition-speed (300 ms). Após a transição o Leaflet
// precisa recalcular o tamanho do contêiner, senão deixa uma faixa cinza.
watch(isCollapsed, () => {
  setTimeout(() => {
    if (map) map.invalidateSize({ animate: false })
  }, 310) // 10 ms de margem além dos 300 ms da transição CSS
})

// ── 7. Marcador de busca geoespacial ─────────────────────────────────────────
watch(
  () => mapStore.geoLocation,
  (loc) => {
    if (searchMarker) {
      map?.removeLayer(searchMarker)
      searchMarker = null
    }
    if (!loc || !map) return

    searchMarker = L.marker([loc.lat, loc.lng], { icon: makeSearchIcon() })
      .addTo(map)
      .bindPopup(`<div class="gs-popup-label">${loc.label}</div>`, {
        className: 'popup-dark',
        maxWidth:  260,
      })
      .openPopup()

    map.flyTo([loc.lat, loc.lng], 13, { duration: 0.8 })
  },
)
</script>

<style scoped>
.map-shell {
  position: relative;
  width: 100%;
  height: 100%;
}

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

:deep(.zoom-btn.is-active) {
  color: var(--text-on-accent);
  background: var(--accent);
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

:deep(.loc-spinner) {
  display: inline-block;
  animation: loc-spin 0.8s linear infinite;
}

@keyframes loc-spin { to { transform: rotate(360deg); } }

/* ── Tooltip de medição ──────────────────────────────────────────────────────── */
:deep(.meas-tooltip) {
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  padding: 0;
}

:deep(.meas-tooltip::before) {
  border-right-color: var(--border-color);
}

:deep(.meas-tip) {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 10px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.72rem;
  color: var(--text-main);
  white-space: nowrap;
}

/* ── Marcador de busca geoespacial ───────────────────────────────────────────── */
/* O divIcon é criado fora da árvore Vue, então :deep é necessário */
:deep(.search-marker-icon) {
  width: 28px;
  height: 36px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  color: var(--accent);
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.6));
}

:deep(.gs-popup-label) {
  font-size: 0.8rem;
  line-height: 1.4;
  padding: 8px 10px;
  color: var(--text-main);
}
</style>