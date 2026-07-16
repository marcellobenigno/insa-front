// src/utils/createDashboardMvtLayer.js
//
// Versão simplificada e independente da renderização de tiles MVT usada em
// MapContainer.vue — cópia proposital, não um refactor compartilhado (decisão
// do usuário: o mini-mapa do dashboard não deve depender do mapStore). Sem
// filtro de busca, sem contagem de matches, opacidade fixa por camada.
import L from 'leaflet'
import { VectorTile } from 'vector-tile'
import Pbf from 'pbf'
import { getThematicColor, parseColor, drawGeometryToContext } from '@/utils/mapRenderer'

/**
 * Cria uma L.GridLayer que busca, decodifica e pinta uma única camada MVT.
 * @param {{ url: string, sourceLayer: string, opacity?: number, zIndex?: number }} options
 */
export function createDashboardMvtLayer({ url, sourceLayer, opacity = 1, zIndex = 1 }) {
  const MvtLayer = L.GridLayer.extend({
    createTile(coords, done) {
      const tile = document.createElement('canvas')
      const size = this.getTileSize()
      tile.width = size.x
      tile.height = size.y
      const ctx = tile.getContext('2d')

      const tileUrl = url.replace('{z}', coords.z).replace('{x}', coords.x).replace('{y}', coords.y)

      fetch(tileUrl)
        .then((res) => {
          if (!res.ok) throw new Error(`Tile PBF não encontrado: ${tileUrl}`)
          return res.arrayBuffer()
        })
        .then((buffer) => {
          try {
            const vt = new VectorTile(new Pbf(new Uint8Array(buffer)))
            const layer = vt.layers[sourceLayer]
            if (!layer) {
              done(null, tile)
              return
            }
            for (let i = 0; i < layer.length; i++) {
              try {
                const feature = layer.feature(i)
                const geom = feature.loadGeometry()
                const rawColor = getThematicColor(sourceLayer, feature.properties)
                const { strokeOnly, color } = parseColor(rawColor)

                drawGeometryToContext(ctx, geom, feature.type, size)

                if (strokeOnly) {
                  ctx.strokeStyle = color
                  ctx.lineWidth = 1.5
                  ctx.globalAlpha = 0.9 * opacity
                  ctx.stroke()
                } else {
                  ctx.fillStyle = color
                  ctx.globalAlpha = 0.8 * opacity
                  ctx.fill()
                }
              } catch {
                // Ignora feições com tipo de geometria não suportado
              }
            }
            done(null, tile)
          } catch (e) {
            console.error('[Dashboard MVT Decode Error]', e)
            done(null, tile)
          }
        })
        .catch((err) => {
          console.error(`[Dashboard MVT Fetch Error] ${tileUrl}:`, err)
          done(null, tile)
        })

      return tile
    },
  })

  return new MvtLayer({ minZoom: 2, maxZoom: 14, zIndex })
}
