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
import gpkgStyles from '@/assets/styles.json'

const mapStore = useMapStore()
const mapEl = ref(null)

let map = null
let currentTileLayer = null
const activeOverlays = new Map() 
const clickReferences = new Map()

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
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
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
              if (!res.ok) throw new Error('Tile não encontrado')
              return res.arrayBuffer()
            })
            .then(buffer => {
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

                if (i === 0) console.log(`Camada: ${sourceLayer} | Atributos reais:`, props)

                const color = getThematicColor(sourceLayer, props)

                ctx.beginPath()
                for (let j = 0; j < geom.length; j++) {
                  const ring = geom[j]
                  for (let k = 0; k < ring.length; k++) {
                    const p = ring[k]
                    const x = (p.x / 4096) * size.x
                    const y = (p.y / 4096) * size.y
                    if (k === 0) ctx.moveTo(x, y)
                    else ctx.lineTo(x, y)
                  }
                  if (feature.type === 3) ctx.closePath()
                }

                ctx.fillStyle = color
                ctx.globalAlpha = 0.8 * currentOpacity
                ctx.fill()

                // ctx.strokeStyle = '#4b5563'
                // ctx.lineWidth = 0.6
                // ctx.globalAlpha = 0.5 * currentOpacity
                // ctx.stroke()
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

      const clickHandler = function(e) {
        if (!mapStore.infoActive[key] || !desired[key]) return

        const zoom = map.getZoom()
        const layerPoint = map.project(e.latlng, zoom).divideBy(256).floor()
        
        const tileUrl = url
          .replace('{z}', zoom)
          .replace('{x}', layerPoint.x)
          .replace('{y}', layerPoint.y)

        fetch(tileUrl)
          .then(res => res.arrayBuffer())
          .then(buffer => {
            const pbf = new Pbf(new Uint8Array(buffer))
            const vt = new VectorTile(pbf)
            const layer = vt.layers[sourceLayer]
            if (!layer) return

            if (layer.length > 0) {
              const props = layer.feature(0).properties
              renderPopup(e.latlng, props, key)
            }
          }).catch(() => {})
      }

      map.on('click', clickHandler)
      clickReferences.set(key, clickHandler)
      activeOverlays.set(key, layer)

    } else if (!shouldBeVisible && isOnMap) {
      map.removeLayer(activeOverlays.get(key))
      activeOverlays.delete(key)

      const oldClickHandler = clickReferences.get(key)
      if (oldClickHandler) {
        map.off('click', oldClickHandler)
        clickReferences.delete(key)
      }
    }
  }
}

// ── 3. Controle Reativo de Opacidade (Chama o Redraw do GridLayer) ─────────────
watch(
  () => mapStore.layerOpacity,
  (opacities) => {
    const baseKey = mapStore.activeBaseLayerKey
    if (currentTileLayer && baseKey in opacities) currentTileLayer.setOpacity(opacities[baseKey])
    
    activeOverlays.forEach((layer) => {
      layer.redraw()
    })
  },
  { deep: true },
)

function renderPopup(latlng, properties, layerKey) {
  const rows = Object.entries(properties)
    .map(([k, v]) => `<tr><td class="gfi-key">${k}</td><td class="gfi-val">${v}</td></tr>`)
    .join('')

  const layerLabel = mapStore.availableOverlays.find(l => l.key === layerKey)?.label || 'Camada'

  const htmlContent = `
    <div class="gfi-popup">
      <div class="gfi-section">
        <div class="gfi-title">${layerLabel}</div>
        <table class="gfi-table">${rows}</table>
      </div>
    </div>`

  L.popup({ className: 'popup-dark', maxWidth: 350 })
    .setLatLng(latlng)
    .setContent(htmlContent)
    .openOn(map)
}

// ── 4. Resolução de Cores Temáticas Vinda do QGIS ─────────────────────────────
function getThematicColor(sourceLayer, featureProps) {
  const layerStyle = gpkgStyles[sourceLayer]
  if (!layerStyle) return '#9ca3af'

  // 🌟 MAPA COMPLETO DOS ATRIBUTOS REAIS EXTRAÍDOS DO CONSOLE:
  const possibleValues = [
    // 1. Pesos e Números Específicos de cada Camada
    featureProps?.IQS,          // Encontrado em iqs_sab_pb
    featureProps?.TipSoilPes,   // Encontrado em solos_tipos_sab_pb_pesos
    featureProps?.SoilTextur,   // Encontrado em textura_sab_pb_pesos
    featureProps?.pes_Peso,     // Encontrado em geologia_sab_pb_pesos
    featureProps?.PesDecl,      // Encontrado em declividade_sab_pb_pesos
    featureProps?.PesosX10Ve,   // Variante encontrada em declividade_sab_pb_pesos
    featureProps?.DN,           // Encontrado em declividade_sab_pb_original
    featureProps?.dn,

    // 2. Colunas de Texto/Descrição originais
    featureProps?.DSC_COMPON,   // Encontrado em solos_tipos_sab_pb_original
    featureProps?.DSC_TEXTUR,   // Encontrado em textura_sab_pb_original
    featureProps?.GLO_DS_LIT,   // Encontrado em geologia_sab_pb_original
    
    // Fallbacks genéricos caso existam em outras camadas
    featureProps?.peso,
    featureProps?.classes,
    featureProps?.textura,
    featureProps?.solo,
    featureProps?.tipo,
    featureProps?.Geologia
  ].filter(v => v !== undefined && v !== null)

  for (let rawVal of possibleValues) {
    // Normaliza o texto removendo espaços em branco especiais do banco de dados (\xa0)
    const valStr = String(rawVal)
      .replace(/\u00a0/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()

    // 🌟 CASO A: Casamento Direto Perfeito (Texto Exato ou Código Inteiro)
    if (layerStyle[valStr]) {
      return layerStyle[valStr]
    }

    // Se for numérico, aplica as aproximações por ponto flutuante ou faixas de valores
    if (!isNaN(Number(valStr))) {
      const numVal = Number(valStr)

      // Coleta todas as chaves do estilo que sejam numéricas e ordena ascendentemente
      const numericKeys = Object.keys(layerStyle)
        .map(k => Number(k.trim()))
        .filter(n => !isNaN(n))
        .sort((a, b) => a - b)

      if (numericKeys.length > 0) {
        // 🌟 CASO B: Intervalos Dinâmicos de Declividade (Ex: DN=10 entra na classe do 16)
        if (sourceLayer.includes('declividade')) {
          const matchedLimit = numericKeys.find(limit => numVal <= limit)
          if (matchedLimit !== undefined) {
            return layerStyle[String(matchedLimit)]
          }
          return layerStyle[String(numericKeys[numericKeys.length - 1])]
        }

        // 🌟 CASO C: Precisão Decimal Flutuante (Ex: Compara 1.5800002 ou 1.58)
        const targetFixed = numVal.toFixed(2)
        const matchingKey = Object.keys(layerStyle).find(key => {
          const cleanKey = String(key).trim()
          return !isNaN(Number(cleanKey)) && Number(cleanKey).toFixed(2) === targetFixed
        })
        if (matchingKey) return layerStyle[matchingKey]
      }
    }
  }

  // 3. Se nenhuma lógica bater, tenta aplicar o padrão definido para a camada ou cinza escuro
  if (layerStyle["default"]) {
    return layerStyle["default"]
  }

  return '#4b5563' // Retorna cinza chumbo se o mapeamento falhar completamente
}
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