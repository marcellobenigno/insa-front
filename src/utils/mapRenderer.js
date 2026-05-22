// src/utils/mapRenderer.js
import gpkgStyles from '@/assets/styles.json'

/**
 * Resolve a cor temática com base nas propriedades da feição e nos estilos do QGIS.
 */
export function getThematicColor(sourceLayer, featureProps) {

  // Blocos de Debug para monitoramento no Console
  if (featureProps && Object.keys(featureProps).length > 0) {
    if (!window._debuggedLayers) window._debuggedLayers = new Set();
    if (!window._debuggedLayers.has(sourceLayer)) {
      window._debuggedLayers.add(sourceLayer);
      console.log(`[WebGIS Debug] Camada ativa detetada: "${sourceLayer}"`);
      console.log(`[WebGIS Debug] Atributos (colunas) reais vindos do MVT para esta camada:`, featureProps);
      console.log(`[WebGIS Debug] Chaves de estilo disponíveis para ela no JSON:`, Object.keys(gpkgStyles[sourceLayer] || {}));
    }
  }

  const layerStyle = gpkgStyles[sourceLayer]
  if (!layerStyle) return '#9ca3af'

  // 🔑 Injeção das novas colunas detectadas no console do navegador
  const possibleValues = [
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

  return layerStyle["default"] || '#4b5563'
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