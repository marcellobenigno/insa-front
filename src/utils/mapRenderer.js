// src/utils/mapRenderer.js
import gpkgStyles from '@/assets/styles.json'

/**
 * Resolve a cor temática com base nas propriedades da feição e nos estilos do QGIS.
 */
export function getThematicColor(sourceLayer, featureProps) {
  const layerStyle = gpkgStyles[sourceLayer]
  if (!layerStyle) return '#9ca3af'

  // 🔑 Injeção das novas colunas detectadas no console do navegador
  const possibleValues = [
    featureProps?.IQC_Pes,
    featureProps?.ETo_Climat,    // ETo Original
    featureProps?.ETo_Pesos,     // ETo Pesos
    featureProps?.IA_climat,     // IA Original
    featureProps?.IA_Pesos,      // IA Pesos
    featureProps?.Clim_Prec,     // Precipitação Original
    featureProps?.Pesos_Prec,    // Precipitação Pesos
    featureProps?.IQS,
    featureProps?.TipSoilPes,
    featureProps?.SoilTextur,
    featureProps?.pes_Peso,
    featureProps?.PesDecl,
    featureProps?.PesosX10Ve,
    featureProps?.DN,
    featureProps?.dn,
    featureProps?.DSC_COMPON,
    featureProps?.DSC_TEXTUR,
    featureProps?.GLO_DS_LIT,
    featureProps?.peso,
    featureProps?.classes,
    featureProps?.textura,
    featureProps?.solo,
    featureProps?.tipo,
    featureProps?.Geologia
  ].filter(v => v !== undefined && v !== null)

  for (let rawVal of possibleValues) {
    const valStr = String(rawVal)
      .replace(/\u00a0/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()

    if (layerStyle[valStr]) {
      return layerStyle[valStr]
    }

    if (!isNaN(Number(valStr))) {
      const numVal = Number(valStr)
      const numericKeys = Object.keys(layerStyle)
        .map(k => Number(k.trim()))
        .filter(n => !isNaN(n))
        .sort((a, b) => a - b)

      if (numericKeys.length > 0) {
        const matchedLimit = numericKeys.find(limit => numVal <= limit)
        
        if (matchedLimit !== undefined) {
          const originalKey = Object.keys(layerStyle).find(k => Number(k.trim()) === matchedLimit)
          if (originalKey) return layerStyle[originalKey]
        }

        const maxKey = Object.keys(layerStyle).find(k => Number(k.trim()) === numericKeys[numericKeys.length - 1])
        if (maxKey) return layerStyle[maxKey]
      }
    }
  }

  // Fallback: "default" explícito → primeiro valor do estilo (símbolo único) → cinza neutro
  return layerStyle["default"] ?? Object.values(layerStyle)[0] ?? '#4b5563'
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