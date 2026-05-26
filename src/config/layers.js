// src/config/layers.js

// ─── CAMADAS BASE (MAPAS DE FUNDO) ────────────────────────────────────────────
export const BASE_LAYERS = {
  osm: {
    label: 'OpenStreetMap',
    meta: 'Global Vector Tile',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    active: false,
  },

  osm_dark: {
    label: 'OpenStreetMap Dark (Carto)',
    meta: 'Dark Vector Tile',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 20,
    active: false,
  },

  satellite_esri: {
    label: 'Satélite (ESRI)',
    meta: 'Imagens de Alta Res.',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution:
      'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, USDA FSA, USGS, Aerogrid, IGN, and the GIS User Community',
    maxZoom: 19,
    active: false,
  },

  google_streets: {
    label: 'Google Streets',
    meta: 'Mapa de Ruas Google',
    url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: false,
  },

  google_satellite: {
    label: 'Google Satellite',
    meta: 'Imagem de Satélite Google',
    url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: true,
  },

  google_hybrid: {
    label: 'Google Hybrid',
    meta: 'Satélite + Labels',
    url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: false,
  },

  google_terrain: {
    label: 'Google Terrain',
    meta: 'Relevo/Terreno Google',
    url: 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: false,
  },
}

// ─── URL BASE DOS VECTOR TILES ────────────────────────────────────────────────
const VECTOR_TILES_URL = import.meta.env.VITE_TILES_URL


// ─── CAMADAS DE SOBREPOSIÇÃO AGRUPADAS POR CATEGORIA ─────────────────────────
//
// Cada categoria possui:
//   key:    identificador único (usado como chave de accordion na sidebar)
//   label:  nome exibido ao usuário
//   color:  cor do ponto indicador na sidebar (CSS color)
//   icon:   classe Bootstrap Icons para o cabeçalho da categoria
//   layers: objeto de camadas (mesma estrutura anterior por camada)
//
export const OVERLAY_CATEGORIES = {

  // 1. Semiárido PB ──────────────────────────────────────────────────────────
  semiarido_pb: {
    label: 'Semiárido PB',
    color: '#f97316',
    icon: 'bi-map',
    layers: {
      municipios_pb_semiarido: {
        label: 'Municípios',
        meta: 'Limites municipais do semiárido paraibano',
        url: VECTOR_TILES_URL,
        sourceLayer: 'municipios_pb_semiarido',
        zIndex: 30,
        active: true,
        searchFields: ['nm_municip'],
        popUpFields:  ['nm_municip', 'cod_ibge_m'],
        fieldTypes:   { nm_municip: 'string', cod_ibge_m: 'string', slug: 'string' },
        descFields:   { nm_municip: 'Município', cod_ibge_m: 'Código IBGE' },
      },
    },
  },

  // 2. Índices de Qualidade ──────────────────────────────────────────────────
  indices_qualidade: {
    label: 'Índices de Qualidade',
    color: '#00d4aa',
    icon: 'bi-graph-up-arrow',
    layers: {
      iqs_sab_pb: {
        label: 'IQS (Qualidade do Solo)',
        meta: 'Índice de Qualidade do Solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'iqs_sab_pb',
        zIndex: 10,
        active: true,
        searchFields: ['IQS'],
        popUpFields:  ['IQS'],
        fieldTypes:   { IQS: 'number' },
        descFields:   { IQS: 'IQS' },
      },
      iqc_sab_pb: {
        label: 'IQC (Capacidade do Solo)',
        meta: 'Índice de Capacidade de Carga',
        url: VECTOR_TILES_URL,
        sourceLayer: 'iqc_sab_pb',
        zIndex: 11,
        active: false,
        searchFields: ['IQC_Pes'],
        popUpFields:  ['IQC_Pes'],
        fieldTypes:   { IQC_Pes: 'number' },
        descFields:   { IQC_Pes: 'IQC_Pes' },
      },
    },
  },

  // 3. Declividade ───────────────────────────────────────────────────────────
  declividade: {
    label: 'Declividade',
    color: '#f59e0b',
    icon: 'bi-bar-chart-steps',
    layers: {
      declividade_sab_pb_original: {
        label: 'Declividade (Original)',
        meta: 'Classes de declividade em %',
        url: VECTOR_TILES_URL,
        sourceLayer: 'declividade_sab_pb_original',
        zIndex: 12,
        active: false,
        searchFields: ['DN'],
        popUpFields:  ['DN'],
        fieldTypes:   { DN: 'number' },
        descFields:   { DN: 'DN' },
      },
      declividade_sab_pb_pesos: {
        label: 'Declividade (Pesos)',
        meta: 'Pesos atribuídos à declividade',
        url: VECTOR_TILES_URL,
        sourceLayer: 'declividade_sab_pb_pesos',
        zIndex: 13,
        active: false,
        searchFields: ['PesDecl', 'PesosX10Ve'],
        popUpFields:  ['PesDecl', 'PesosX10Ve'],
        fieldTypes:   { PesDecl: 'number', PesosX10Ve: 'number' },
        descFields:   { PesDecl: 'PesDecl', PesosX10Ve: 'PesosX10Ve' },
      },
    },
  },

  // 4. Geologia ──────────────────────────────────────────────────────────────
  geologia: {
    label: 'Geologia',
    color: '#8b5cf6',
    icon: 'bi-layers',
    layers: {
      geologia_sab_pb_original: {
        label: 'Geologia (Original)',
        meta: 'Formações litológicas e rochas',
        url: VECTOR_TILES_URL,
        sourceLayer: 'geologia_sab_pb_original',
        zIndex: 15,
        active: false,
        searchFields: ['GLO_DS_LIT'],
        popUpFields:  ['GLO_DS_LIT'],
        fieldTypes:   { GLO_DS_LIT: 'string' },
        descFields:   { GLO_DS_LIT: 'GLO_DS_LIT' },
      },
      geologia_sab_pb_pesos: {
        label: 'Geologia (Pesos)',
        meta: 'Pesos atribuídos às formações rochosas',
        url: VECTOR_TILES_URL,
        sourceLayer: 'geologia_sab_pb_pesos',
        zIndex: 16,
        active: false,
        searchFields: ['GLO_DS_LIT', 'pes_Peso'],
        popUpFields:  ['GLO_DS_LIT', 'pes_Peso'],
        fieldTypes:   { GLO_DS_LIT: 'string', pes_Peso: 'number' },
        descFields:   { GLO_DS_LIT: 'GLO_DS_LIT', pes_Peso: 'pes_Peso' },
      },
    },
  },

  // 5. Solos ─────────────────────────────────────────────────────────────────
  solos: {
    label: 'Solos',
    color: '#ec4899',
    icon: 'bi-geo',
    layers: {
      solos_tipos_sab_pb_original: {
        label: 'Tipos de Solos (Original)',
        meta: 'Classificação pedológica (SiBCS)',
        url: VECTOR_TILES_URL,
        sourceLayer: 'solos_tipos_sab_pb_original',
        zIndex: 17,
        active: false,
        searchFields: ['DSC_COMPON'],
        popUpFields:  ['DSC_COMPON'],
        fieldTypes:   { DSC_COMPON: 'string' },
        descFields:   { DSC_COMPON: 'DSC_COMPON' },
      },
      solos_tipos_sab_pb_pesos: {
        label: 'Tipos de Solos (Pesos)',
        meta: 'Pesos atribuídos aos tipos de solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'solos_tipos_sab_pb_pesos',
        zIndex: 18,
        active: false,
        searchFields: ['DSC_COMPON', 'TipSoilPes'],
        popUpFields:  ['DSC_COMPON', 'TipSoilPes'],
        fieldTypes:   { DSC_COMPON: 'string', TipSoilPes: 'number' },
        descFields:   { DSC_COMPON: 'DSC_COMPON', TipSoilPes: 'TipSoilPes' },
      },
      textura_sab_pb_original: {
        label: 'Textura do Solo (Original)',
        meta: 'Grupamento de textura física',
        url: VECTOR_TILES_URL,
        sourceLayer: 'textura_sab_pb_original',
        zIndex: 19,
        active: false,
        searchFields: ['DSC_TEXTUR'],
        popUpFields:  ['DSC_TEXTUR'],
        fieldTypes:   { DSC_TEXTUR: 'string' },
        descFields:   { DSC_TEXTUR: 'DSC_TEXTUR' },
      },
      textura_sab_pb_pesos: {
        label: 'Textura do Solo (Pesos)',
        meta: 'Pesos atribuídos à textura do solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'textura_sab_pb_pesos',
        zIndex: 20,
        active: false,
        searchFields: ['DSC_TEXTUR', 'SoilTextur'],
        popUpFields:  ['DSC_TEXTUR', 'SoilTextur'],
        fieldTypes:   { DSC_TEXTUR: 'string', SoilTextur: 'number' },
        descFields:   { DSC_TEXTUR: 'DSC_TEXTUR', SoilTextur: 'SoilTextur' },
      },
    },
  },

  // 6. Agroclimatologia ──────────────────────────────────────────────────────
  agroclimatologia: {
    label: 'Agroclimatologia',
    color: '#3b82f6',
    icon: 'bi-cloud-rain',
    layers: {
      eto_sab_pb_original: {
        label: 'Evapotranspiração (ETo)',
        meta: 'Evapotranspiração de referência acumulada',
        url: VECTOR_TILES_URL,
        sourceLayer: 'eto_sab_pb_original',
        zIndex: 21,
        active: false,
        searchFields: ['ETo_Climat'],
        popUpFields:  ['ETo_Climat'],
        fieldTypes:   { ETo_Climat: 'number' },
        descFields:   { ETo_Climat: 'ETo_Climat' },
      },
      eto_sab_pb_pesos: {
        label: 'Evapotranspiração (Pesos)',
        meta: 'Pesos atribuídos à ETo regional',
        url: VECTOR_TILES_URL,
        sourceLayer: 'eto_sab_pb_pesos',
        zIndex: 22,
        active: false,
        searchFields: ['ETo_Pesos'],
        popUpFields:  ['ETo_Pesos'],
        fieldTypes:   { ETo_Pesos: 'number' },
        descFields:   { ETo_Pesos: 'ETo_Pesos' },
      },
      ia_sab_pb_original: {
        label: 'Índice de Aridez (IA)',
        meta: 'Índice de aridez meteorológica',
        url: VECTOR_TILES_URL,
        sourceLayer: 'ia_sab_pb_original',
        zIndex: 23,
        active: false,
        searchFields: ['IA_climat'],
        popUpFields:  ['IA_climat'],
        fieldTypes:   { IA_climat: 'number' },
        descFields:   { IA_climat: 'IA_climat' },
      },
      ia_sab_pb_pesos: {
        label: 'Índice de Aridez (Pesos)',
        meta: 'Pesos atribuídos ao Índice de Aridez',
        url: VECTOR_TILES_URL,
        sourceLayer: 'ia_sab_pb_pesos',
        zIndex: 24,
        active: false,
        searchFields: ['IA_Pesos'],
        popUpFields:  ['IA_Pesos'],
        fieldTypes:   { IA_Pesos: 'number' },
        descFields:   { IA_Pesos: 'IA_Pesos' },
      },
      precipitacao_sab_pb_original: {
        label: 'Precipitação Pluviométrica',
        meta: 'Precipitação média anual acumulada',
        url: VECTOR_TILES_URL,
        sourceLayer: 'precipitacao_sab_pb_original',
        zIndex: 25,
        active: false,
        searchFields: ['Clim_Prec'],
        popUpFields:  ['Clim_Prec'],
        fieldTypes:   { Clim_Prec: 'number' },
        descFields:   { Clim_Prec: 'Clim_Prec' },
      },
      precipitacao_sab_pb_pesos: {
        label: 'Precipitação (Pesos)',
        meta: 'Pesos atribuídos às faixas de chuva',
        url: VECTOR_TILES_URL,
        sourceLayer: 'precipitacao_sab_pb_pesos',
        zIndex: 26,
        active: false,
        searchFields: ['Pesos_Prec'],
        popUpFields:  ['Pesos_Prec'],
        fieldTypes:   { Pesos_Prec: 'number' },
        descFields:   { Pesos_Prec: 'Pesos_Prec' },
      },
    },
  },
}

// ─── OVERLAY_LAYERS PLANO (retrocompatibilidade com mapStore / MapContainer) ──
//
// Gerado automaticamente a partir de OVERLAY_CATEGORIES para que MapContainer.vue
// e mapStore.js não precisem ser reescritos. Qualquer novo código deve preferir
// consumir OVERLAY_CATEGORIES diretamente.
//
export const OVERLAY_LAYERS = Object.fromEntries(
  Object.values(OVERLAY_CATEGORIES).flatMap(cat =>
    Object.entries(cat.layers)
  )
)