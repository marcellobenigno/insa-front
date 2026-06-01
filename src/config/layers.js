// src/config/layers.js

// ─── CAMADAS BASE (MAPAS DE FUNDO) ────────────────────────────────────────────
export const BASE_LAYERS = {
  google_satellite: {
    label: 'Google Satellite',
    meta: 'Imagem de Satélite Google',
    url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: true,
  },

  google_streets: {
    label: 'Google Streets',
    meta: 'Mapa de Ruas Google',
    url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attribution: '&copy; Google',
    maxZoom: 20,
    active: false,
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
}

// ─── URL BASE DOS VECTOR TILES ────────────────────────────────────────────────
const VECTOR_TILES_URL = import.meta.env.VITE_TILES_URL


// ─── CAMADAS DE SOBREPOSIÇÃO AGRUPADAS POR CATEGORIA ─────────────────────────
//
// Cada categoria possui:
//   key:    identificador único (usado como chave de accordion na sidebar)
//   label:  nome exibido ao usuário

//   icon:   classe Bootstrap Icons para o cabeçalho da categoria
//   layers: objeto de camadas (mesma estrutura anterior por camada)
//
export const OVERLAY_CATEGORIES = {

  // 1. Semiárido PB ──────────────────────────────────────────────────────────
  semiarido_pb: {
    label: 'Semiárido PB',
    icon: 'bi-map',
    layers: {
      municipios_pb_semiarido: {
        label: 'Municípios',
        meta: 'Limites Municipais do Semiárido Paraibano',
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

  // 2. Indicadores de Qualidade ─────────────────────────────────────────────
  indices_qualidade: {
    label: 'Indicadores de Qualidade',
    icon: 'bi-graph-up-arrow',
    layers: {
      iqs_sab_pb: {
        label: 'Índice de Qualidade do Solo (IQS)',
        meta: 'Índice de Qualidade do Solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'iqs_sab_pb',
        zIndex: 10,
        active: true,
        searchFields: ['IQS'],
        popUpFields:  ['IQS'],
        fieldTypes:   { IQS: 'number' },
        descFields:   { IQS: 'Índice de Qualidade do Solo' },
      },
      iqc_sab_pb: {
        label: 'Índice de Qualidade Climática (IQC)',
        meta: 'Índice de Qualidade Climática',
        url: VECTOR_TILES_URL,
        sourceLayer: 'iqc_sab_pb',
        zIndex: 11,
        active: false,
        searchFields: ['IQC_Pes'],
        popUpFields:  ['IQC_Pes'],
        fieldTypes:   { IQC_Pes: 'number' },
        descFields:   { IQC_Pes: 'Índice de Qualidade Climática' },
      },
    },
  },

  // 3. Declividade ───────────────────────────────────────────────────────────
  declividade: {
    label: 'Declividade',
    icon: 'bi-bar-chart-steps',
    layers: {
      declividade_sab_pb_original: {
        label: 'Declividade',
        meta: 'Classes de declividade em %',
        url: VECTOR_TILES_URL,
        sourceLayer: 'declividade_sab_pb_original',
        zIndex: 12,
        active: false,
        searchFields: ['DN'],
        popUpFields:  ['DN'],
        fieldTypes:   { DN: 'number' },
        descFields:   { DN: 'Declividade (%)' },
      },
      declividade_sab_pb_pesos: {
        label: 'Declividade (Escores de Qualidade)',
        meta: 'Escores de qualidade atribuídos à declividade',
        url: VECTOR_TILES_URL,
        sourceLayer: 'declividade_sab_pb_pesos',
        zIndex: 13,
        active: false,
        searchFields: ['PesDecl'],
        popUpFields:  ['PesDecl'],
        fieldTypes:   { PesDecl: 'number' },
        descFields:   { PesDecl: 'Escore de Qualidade da Declividade' },
      },
    },
  },

  // 4. Geologia ──────────────────────────────────────────────────────────────
  geologia: {
    label: 'Geologia',
    icon: 'bi-layers',
    layers: {
      geologia_sab_pb_original: {
        label: 'Geologia',
        meta: 'Formações litológicas e rochas',
        url: VECTOR_TILES_URL,
        sourceLayer: 'geologia_sab_pb_original',
        zIndex: 15,
        active: false,
        searchFields: ['GLO_DS_LIT'],
        popUpFields:  ['GLO_DS_LIT'],
        fieldTypes:   { GLO_DS_LIT: 'string' },
        descFields:   { GLO_DS_LIT: 'Descrição Litológica' },
      },
      geologia_sab_pb_pesos: {
        label: 'Geologia (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuídos às formações rochosas',
        url: VECTOR_TILES_URL,
        sourceLayer: 'geologia_sab_pb_pesos',
        zIndex: 16,
        active: false,
        searchFields: ['GLO_DS_LIT', 'pes_Peso'],
        popUpFields:  ['GLO_DS_LIT', 'pes_Peso'],
        fieldTypes:   { GLO_DS_LIT: 'string', pes_Peso: 'number' },
        descFields:   { GLO_DS_LIT: 'Descrição Litológica', pes_Peso: 'Escores de Qualidade (Geologia)' },
      },
    },
  },

  // 5. Solos ─────────────────────────────────────────────────────────────────
  solos: {
    label: 'Solos',
    icon: 'bi-geo',
    layers: {
      solos_tipos_sab_pb_original: {
        label: 'Tipos de Solos',
        meta: 'Classificação pedológica (SiBCS)',
        url: VECTOR_TILES_URL,
        sourceLayer: 'solos_tipos_sab_pb_original',
        zIndex: 17,
        active: false,
        searchFields: ['DSC_COMPON'],
        popUpFields:  ['DSC_COMPON'],
        fieldTypes:   { DSC_COMPON: 'string' },
        descFields:   { DSC_COMPON: 'Componente Pedológico' },
      },
      solos_tipos_sab_pb_pesos: {
        label: 'Tipos de Solos (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuídos aos tipos de solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'solos_tipos_sab_pb_pesos',
        zIndex: 18,
        active: false,
        searchFields: ['DSC_COMPON', 'TipSoilPes'],
        popUpFields:  ['DSC_COMPON', 'TipSoilPes'],
        fieldTypes:   { DSC_COMPON: 'string', TipSoilPes: 'number' },
        descFields:   { DSC_COMPON: 'Componente Pedológico', TipSoilPes: 'Escores de Qualidade do Tipo de Solo' },
      },
      textura_sab_pb_original: {
        label: 'Textura do Solo',
        meta: 'Grupamento de textura física',
        url: VECTOR_TILES_URL,
        sourceLayer: 'textura_sab_pb_original',
        zIndex: 19,
        active: false,
        searchFields: ['DSC_TEXTUR'],
        popUpFields:  ['DSC_TEXTUR'],
        fieldTypes:   { DSC_TEXTUR: 'string' },
        descFields:   { DSC_TEXTUR: 'Textura do Solo' },
      },
      textura_sab_pb_pesos: {
        label: 'Textura do Solo (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuídos à textura do solo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'textura_sab_pb_pesos',
        zIndex: 20,
        active: false,
        searchFields: ['DSC_TEXTUR', 'SoilTextur'],
        popUpFields:  ['DSC_TEXTUR', 'SoilTextur'],
        fieldTypes:   { DSC_TEXTUR: 'string', SoilTextur: 'number' },
        descFields:   { DSC_TEXTUR: 'Textura do Solo', SoilTextur: 'Escores de Qualidade da Textura' },
      },
    },
  },

  // 6. Climatologia ─────────────────────────────────────────────────────────
  agroclimatologia: {
    label: 'Climatologia',
    icon: 'bi-cloud-rain',
    layers: {
      eto_sab_pb_original: {
        label: 'Evapotranspiração (ETo)',
        meta: 'Evapotranspiração de referência acumulada (climatologia 1996-2025)',
        url: VECTOR_TILES_URL,
        sourceLayer: 'eto_sab_pb_original',
        zIndex: 21,
        active: false,
        searchFields: ['ETo_Climat'],
        popUpFields:  ['ETo_Climat'],
        fieldTypes:   { ETo_Climat: 'number' },
        descFields:   { ETo_Climat: 'ETo Climatologia (1996-2025) (mm/ano)' },
      },
      eto_sab_pb_pesos: {
        label: 'Evapotranspiração (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuídos à ETo',
        url: VECTOR_TILES_URL,
        sourceLayer: 'eto_sab_pb_pesos',
        zIndex: 22,
        active: false,
        searchFields: ['ETo_Pesos'],
        popUpFields:  ['ETo_Pesos'],
        fieldTypes:   { ETo_Pesos: 'number' },
        descFields:   { ETo_Pesos: 'Escore de Qualidade ETo' },
      },
      ia_sab_pb_original: {
        label: 'Índice de Aridez (IA)',
        meta: 'Índice de aridez (climatologia 1996-2025)',
        url: VECTOR_TILES_URL,
        sourceLayer: 'ia_sab_pb_original',
        zIndex: 23,
        active: false,
        searchFields: ['IA_climat'],
        popUpFields:  ['IA_climat'],
        fieldTypes:   { IA_climat: 'number' },
        descFields:   { IA_climat: 'Índice de Aridez' },
      },
      ia_sab_pb_pesos: {
        label: 'Índice de Aridez (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuídos ao Índice de Aridez',
        url: VECTOR_TILES_URL,
        sourceLayer: 'ia_sab_pb_pesos',
        zIndex: 24,
        active: false,
        searchFields: ['IA_Pesos'],
        popUpFields:  ['IA_Pesos'],
        fieldTypes:   { IA_Pesos: 'number' },
        descFields:   { IA_Pesos: 'Escore de Qualidade IA' },
      },
      precipitacao_sab_pb_original: {
        label: 'Precipitação Pluviométrica',
        meta: 'Precipitação acumulada anual (climatologia 1996-2025)',
        url: VECTOR_TILES_URL,
        sourceLayer: 'precipitacao_sab_pb_original',
        zIndex: 25,
        active: false,
        searchFields: ['Clim_Prec'],
        popUpFields:  ['Clim_Prec'],
        fieldTypes:   { Clim_Prec: 'number' },
        descFields:   { Clim_Prec: 'Precipitação Climatologia (1996-2025) (mm/ano)' },
      },
      precipitacao_sab_pb_pesos: {
        label: 'Precipitação (Escores de Qualidade)',
        meta: 'Escores de Qualidade atribuída a Precipitação acumulada anual',
        url: VECTOR_TILES_URL,
        sourceLayer: 'precipitacao_sab_pb_pesos',
        zIndex: 26,
        active: false,
        searchFields: ['Pesos_Prec'],
        popUpFields:  ['Pesos_Prec'],
        fieldTypes:   { Pesos_Prec: 'number' },
        descFields:   { Pesos_Prec: 'Escore de Qualidade Precipitação' },
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
