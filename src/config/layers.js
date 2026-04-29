// ─── Utilitário ───────────────────────────────────────────────────────────────

/**
 * Gera a URL do GetLegendGraphic para uma camada publicada no GeoServer.
 * @param {string} geoServerUrl  URL base do serviço WMS
 * @param {string} layerName     Nome qualificado da camada (ex.: "insa:municipios_semiarido")
 */
export function getLegendUrl(geoServerUrl, layerName) {
  return (
    `${geoServerUrl}?REQUEST=GetLegendGraphic&` +
    'VERSION=1.1.0&' +
    'FORMAT=image/png&' +
    'WIDTH=18&' +
    'HEIGHT=18&' +
    `LAYER=${layerName}&` +
    'LEGEND_OPTIONS=fontName:Arial;fontAntiAliasing:true;dpi=200'
  )
}

// ─── Camadas Base ─────────────────────────────────────────────────────────────

/**
 * active: true  →  camada selecionada ao inicializar o mapa (somente uma deve ser true)
 */
export const BASE_LAYERS = {
  osm: {
    label: 'OpenStreetMap',
    meta: 'Global Vector Tile',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    active: true,
  },
  osm_dark: {
    label: 'OpenStreetMap Dark (Carto)',
    meta: 'Dark Vector Tile',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19,
    active: false,
  },
  satellite: {
    label: 'Satélite (ESRI)',
    meta: 'Imagens de Alta Res.',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution:
      'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18,
    active: false,
  },
}

// ─── Camadas de Sobreposição WMS ──────────────────────────────────────────────

const GEOSERVER_URL = 'http://localhost:8080/geoserver/insa/wms'

/**
 * active       →  visível ao inicializar o mapa
 * searchFields →  colunas usadas em buscas/filtros (Entrega 4)
 * legend       →  URL GetLegendGraphic para exibir na sidebar
 */
export const OVERLAY_LAYERS = {
  municipios_semiarido: {
    label: 'Municípios do Semiárido',
    meta: 'IBGE 2024',
    geoServerUrl: GEOSERVER_URL,
    wmsLayer: 'insa:municipios_semiarido',
    attribution: '&copy; <a href="https://www.ibge.gov.br/">IBGE</a>',
    maxZoom: 19,
    minZoom: 1,
    zIndex: 10,
    active: true,
    searchFields: ['geocodigo', 'municipio'],
    legend: getLegendUrl(GEOSERVER_URL, 'insa:municipios_semiarido'),
  },
  limite_semiarido: {
    label: 'Limite do Semiárido',
    meta: 'INSA 2024',
    geoServerUrl: GEOSERVER_URL,
    wmsLayer: 'insa:limite_semiarido',
    attribution: '&copy; <a href="https://www.ibge.gov.br/">IBGE</a>',
    maxZoom: 19,
    minZoom: 1,
    zIndex: 11,
    active: true,
    searchFields: [],
    legend: getLegendUrl(GEOSERVER_URL, 'insa:limite_semiarido'),
  },
}
