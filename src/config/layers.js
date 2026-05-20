// ─── UTILIÁRIO OBSOLETO (MANTIDO CASO OUTRO COMPONENTE PRECISE) ────────────────
/**
 * Nota de Migração: As camadas Vector Tiles não utilizam mais essa função,
 * pois os atributos agora são lidos localmente direto do binário .pbf.
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

// ─── CAMADAS BASE (MAPAS DE FUNDO) ────────────────────────────────────────────
export const BASE_LAYERS = {
  osm: {
    label: 'OpenStreetMap',
    meta: 'Global Vector Tile',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    active: true,
  },
  osm_dark: {
    label: 'OpenStreetMap Dark (Carto)',
    meta: 'Dark Vector Tile',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 20,
    active: false,
  },
  satellite: {
    label: 'Satélite (ESRI)',
    meta: 'Imagens de Alta Res.',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18,
    active: false,
  },
}

// ─── CAMADAS DE SOBREPOSIÇÃO (VECTOR TILES DA PASTA PUBLIC) ───────────────────
/**
 * Rota estática que o Vite serve a partir da sua pasta public.
 * O Leaflet substituirá automaticamente {z}, {x} e {y} em tempo de execução
 * para buscar os micro-arquivos binários à medida que o usuário navega pelo mapa.
 */
const VECTOR_TILES_URL = '/tiles/insa_layers/{z}/{x}/{y}.pbf'

export const OVERLAY_LAYERS = {
  // 1. Camadas de Declividade
  declividade_sab_pb: {
    label: 'Declividade (Geral)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb', // Nome exato gerado pelo Tippecanoe
    zIndex: 10,
    active: false,
    searchFields: ['peso', 'classe'],
  },
  declividade_sab_pb_original: {
    label: 'Declividade (Malha Original)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb_original',
    zIndex: 11,
    active: false,
    searchFields: ['classe'],
  },
  declividade_sab_pb_pesos: {
    label: 'Declividade (Pesos Configurados)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb_pesos',
    zIndex: 12,
    active: false,
    searchFields: ['peso'],
  },

  // 2. Camadas de Geologia
  geologia_sab_pb_original: {
    label: 'Geologia (Malha Original)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'geologia_sab_pb_original',
    zIndex: 13,
    active: false,
    searchFields: ['sigla', 'formacao'],
  },
  geologia_sab_pb_pesos: {
    label: 'Geologia (Pesos Configurados)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'geologia_sab_pb_pesos',
    zIndex: 14,
    active: false,
    searchFields: ['peso', 'classe'],
  },

  // 3. Camada de IQS
  iqs_sab_pb: {
    label: 'Índice de Qualidade do Solo (IQS)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'iqs_sab_pb',
    zIndex: 15,
    active: false,
    searchFields: ['iqs_valor', 'status'],
  },

  // 4. Camadas de Solos Tipos
  solos_tipos_sab_pb_original: {
    label: 'Tipos de Solos (Original)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'solos_tipos_sab_pb_original',
    zIndex: 16,
    active: false,
    searchFields: ['componente', 'ordem'],
  },
  solos_tipos_sab_pb_pesos: {
    label: 'Tipos de Solos (Pesos Configurados)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'solos_tipos_sab_pb_pesos',
    zIndex: 17,
    active: false,
    searchFields: ['peso'],
  },

  // 5. Camadas de Textura do Solo
  textura_sab_pb_original: {
    label: 'Textura do Solo (Original)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'textura_sab_pb_original',
    zIndex: 18,
    active: false,
    searchFields: ['componente', 'grupamento'],
  },
  textura_sab_pb_pesos: {
    label: 'Textura do Solo (Pesos Configurados)',
    meta: 'INSA Vetorial Otimizado',
    url: VECTOR_TILES_URL,
    sourceLayer: 'textura_sab_pb_pesos',
    zIndex: 19,
    active: false,
    searchFields: ['peso'],
  }
}