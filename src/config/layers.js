// src/config/layers.js

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
  // 1. Índices de Qualidade (Resultados Analíticos Principais)
  iqs_sab_pb: {
    label: 'IQS (Qualidade do Solo)',
    meta: 'Índice de Qualidade do Solo',
    url: VECTOR_TILES_URL,
    sourceLayer: 'iqs_sab_pb',
    zIndex: 10,
    active: true,
    searchFields: ['iqs_valor', 'status'],
  },
  iqc_sab_pb: {
    label: 'IQC (Capacidade do Solo)',
    meta: 'Índice de Capacidade de Carga',
    url: VECTOR_TILES_URL,
    sourceLayer: 'iqc_sab_pb',
    zIndex: 11,
    active: false,
    searchFields: ['valor', 'classe'],
  },

  // 2. Camadas de Declividade (Morfologia e Relevo)
  declividade_sab_pb_original: {
    label: 'Declividade (Original)',
    meta: 'Classes de declividade em %',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb_original',
    zIndex: 12,
    active: false,
    searchFields: ['classe'],
  },
  declividade_sab_pb_pesos: {
    label: 'Declividade (Pesos)',
    meta: 'Pesos atribuídos à declividade',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb_pesos',
    zIndex: 13,
    active: false,
    searchFields: ['peso'],
  },
  declividade_sab_pb: {
    label: 'Declividade (Geral)',
    meta: 'Grade geral de declividade',
    url: VECTOR_TILES_URL,
    sourceLayer: 'declividade_sab_pb', 
    zIndex: 14,
    active: false,
    searchFields: ['peso', 'classe'],
  },

  // 3. Camadas de Geologia (Material de Origem / Litologia)
  geologia_sab_pb_original: {
    label: 'Geologia (Original)',
    meta: 'Formações litológicas e rochas',
    url: VECTOR_TILES_URL,
    sourceLayer: 'geologia_sab_pb_original',
    zIndex: 15,
    active: false,
    searchFields: ['sigla', 'formacao'],
  },
  geologia_sab_pb_pesos: {
    label: 'Geologia (Pesos)',
    meta: 'Pesos atribuídos às formações rochosas',
    url: VECTOR_TILES_URL,
    sourceLayer: 'geologia_sab_pb_pesos',
    zIndex: 16,
    active: false,
    searchFields: ['peso', 'classe'],
  },

  // 4. Camadas de Classificação de Solos (Tipologia Pedológica)
  solos_tipos_sab_pb_original: {
    label: 'Tipos de Solos (Original)',
    meta: 'Classificação pedológica (SiBCS)',
    url: VECTOR_TILES_URL,
    sourceLayer: 'solos_tipos_sab_pb_original',
    zIndex: 17,
    active: false,
    searchFields: ['componente', 'ordem'],
  },
  solos_tipos_sab_pb_pesos: {
    label: 'Tipos de Solos (Pesos)',
    meta: 'Pesos atribuídos aos tipos de solo',
    url: VECTOR_TILES_URL,
    sourceLayer: 'solos_tipos_sab_pb_pesos',
    zIndex: 18,
    active: false,
    searchFields: ['peso'],
  },

  // 5. Camadas de Textura Físico-Química do Solo
  textura_sab_pb_original: {
    label: 'Textura do Solo (Original)',
    meta: 'Grupamento de textura física',
    url: VECTOR_TILES_URL,
    sourceLayer: 'textura_sab_pb_original',
    zIndex: 19,
    active: false,
    searchFields: ['componente', 'grupamento'],
  },
  textura_sab_pb_pesos: {
    label: 'Textura do Solo (Pesos)',
    meta: 'Pesos atribuídos à textura do solo',
    url: VECTOR_TILES_URL,
    sourceLayer: 'textura_sab_pb_pesos',
    zIndex: 20,
    active: false,
    searchFields: ['peso'],
  },

  // 6. Agroclimatologia e Hidrologia (Camadas Adicionadas)
  eto_sab_pb_original: {
    label: 'Evapotranspiração (ETo)',
    meta: 'Evapotranspiração de referência acumulada',
    url: VECTOR_TILES_URL,
    sourceLayer: 'eto_sab_pb_original',
    zIndex: 21,
    active: false,
    searchFields: ['valor', 'classe'],
  },
  eto_sab_pb_pesos: {
    label: 'Evapotranspiração (Pesos)',
    meta: 'Pesos atribuídos à ETo regional',
    url: VECTOR_TILES_URL,
    sourceLayer: 'eto_sab_pb_pesos',
    zIndex: 22,
    active: false,
    searchFields: ['peso'],
  },
  ia_sab_pb_original: {
    label: 'Índice de Aridez (IA)',
    meta: 'Índice de aridez meteorológica',
    url: VECTOR_TILES_URL,
    sourceLayer: 'ia_sab_pb_original',
    zIndex: 23,
    active: false,
    searchFields: ['valor', 'status'],
  },
  ia_sab_pb_pesos: {
    label: 'Índice de Aridez (Pesos)',
    meta: 'Pesos atribuídos ao Índice de Aridez',
    url: VECTOR_TILES_URL,
    sourceLayer: 'ia_sab_pb_pesos',
    zIndex: 24,
    active: false,
    searchFields: ['peso'],
  },
  precipitacao_sab_pb_original: {
    label: 'Precipitação Pluviométrica',
    meta: 'Precipitação média anual acumulada',
    url: VECTOR_TILES_URL,
    sourceLayer: 'precipitacao_sab_pb_original',
    zIndex: 25,
    active: false,
    searchFields: ['valor', 'classe'],
  },
  precipitacao_sab_pb_pesos: {
    label: 'Precipitação (Pesos)',
    meta: 'Pesos atribuídos às faixas de chuva',
    url: VECTOR_TILES_URL,
    sourceLayer: 'precipitacao_sab_pb_pesos',
    zIndex: 26,
    active: false,
    searchFields: ['peso'],
  }
}