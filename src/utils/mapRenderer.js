// src/utils/mapRenderer.js
import gpkgStyles from '@/assets/styles.json'

/**
 * Resolve a cor temática com base nas propriedades da feição e nos estilos do QGIS.
 *
 * `styles.json` guarda, por camada, o tipo de classificação do QGIS
 * ("categorized": correspondência exata de valor; "graduated": faixas por
 * limite superior; "stroke"/"single": cor fixa) e o campo (`field`) usado
 * para classificar — ambos extraídos diretamente do QML pelo `scripts/styles.py`.
 */
export function getThematicColor(sourceLayer, featureProps) {
  const style = gpkgStyles[sourceLayer]
  if (!style || !style.classes?.length) return '#9ca3af'

  if (style.type === 'stroke') return `stroke:${style.classes[0].color}`
  if (style.type === 'single') return style.classes[0].color

  const numVal = Number(featureProps?.[style.field])
  if (Number.isNaN(numVal)) return '#9ca3af'

  if (style.type === 'categorized') {
    let best = style.classes[0]
    let bestDiff = Math.abs(numVal - best.value)
    for (const c of style.classes) {
      const diff = Math.abs(numVal - c.value)
      if (diff < bestDiff) { best = c; bestDiff = diff }
    }
    return best.color
  }

  // graduated: primeira classe cujo limite superior comporta o valor
  for (const c of style.classes) {
    if (numVal <= c.max + 1e-6) return c.color
  }
  return style.classes[style.classes.length - 1].color
}

/**
 * Avalia se as propriedades de uma feição satisfazem um filtro de busca.
 * Para campos numéricos usa operadores relacionais; para texto usa "contém" (case-insensitive).
 *
 * @param {object} featureProps  Propriedades da feição MVT
 * @param {{ field: string, operator: string, value: string }} filter
 * @returns {boolean}
 */
export function matchesFilter(featureProps, filter) {
  if (!filter || !filter.value) return true
  const { field, operator, value } = filter
  const raw = featureProps?.[field]
  if (raw === undefined || raw === null) return false

  const numSearch = parseFloat(value)
  const numFeature = parseFloat(raw)

  if (!isNaN(numSearch) && !isNaN(numFeature)) {
    switch (operator) {
      case '=':  return numFeature === numSearch
      case '>':  return numFeature >   numSearch
      case '>=': return numFeature >=  numSearch
      case '<':  return numFeature <   numSearch
      case '<=': return numFeature <=  numSearch
      default:   return false
    }
  }

  // Texto: busca parcial insensível a maiúsculas
  return String(raw).toLowerCase().includes(String(value).toLowerCase())
}

/**
 * Verifica se a cor indica um estilo stroke-only (ex: "stroke:#918e90").
 * Retorna { strokeOnly: true, color: '#918e90' } ou { strokeOnly: false, color }.
 */
export function parseColor(colorValue) {
  if (typeof colorValue === 'string' && colorValue.startsWith('stroke:')) {
    return { strokeOnly: true, color: colorValue.slice(7) }
  }
  return { strokeOnly: false, color: colorValue }
}

/**
 * Desenha as geometrias de uma feição MVT em um contexto Canvas 2D.
 */
export function drawGeometryToContext(ctx, geom, featureType, tileSize) {
  ctx.beginPath()
  for (let j = 0; j < geom.length; j++) {
    const ring = geom[j]
    for (let k = 0; k < ring.length; k++) {
      const p = ring[k]
      const x = (p.x / 4096) * tileSize.x
      const y = (p.y / 4096) * tileSize.y
      if (k === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    if (featureType === 3) ctx.closePath() // Polígono
  }
}
