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


// ─── CAMADAS DE SOBREPOSIÇÃO EM ÁRVORE HIERÁRQUICA ───────────────────────────
//
// OVERLAY_TREE é uma lista de nós recursivos. Cada nó é um dos dois formatos:
//
//   Nó de grupo (accordion, sem camada própria):
//     { key, label, icon, layer: null, children: [ ...nós ] }
//
//   Nó folha (uma camada de fato, renderizada como LayerCard):
//     { key, layer: { label, meta, url, sourceLayer, zIndex, active,
//                      searchFields, popUpFields, fieldTypes, descFields } }
//
// A ordem de cada array `children` É a ordem exibida na sidebar — não há
// reordenação em tempo de execução, então a ordem aqui deve refletir
// exatamente a hierarquia do projeto (Semiárido → Índices de Qualidade →
// IQS/IQV/IQC/IQM → Escores de Qualidade → camada).
//
export const OVERLAY_TREE = [

  // 1. Limites ───────────────────────────────────────────────────────────────
  {
    key: 'semiarido_pb',
    label: 'Limites',
    icon: 'bi-map',
    layer: null,
    children: [
      {
        key: 'limite_semiarido_pb',
        layer: {
          label: 'Limites do Semiárido PB',
          meta: 'Contorno da região do Semiárido Paraibano',
          url: VECTOR_TILES_URL,
          sourceLayer: 'limite_semiarido_pb',
          zIndex: 36,
          active: true,
          noPopup: true,
        },
      },
      {
        key: 'municipios_pb_semiarido',
        layer: {
          label: 'Municípios do Semiárido',
          meta: 'Limites Municipais do Semiárido Paraibano',
          url: VECTOR_TILES_URL,
          sourceLayer: 'municipios_pb_semiarido',
          zIndex: 32,
          active: true,
          searchFields: ['nm_municip'],
          popUpFields:  ['nm_municip', 'cod_ibge_m'],
          fieldTypes:   { nm_municip: 'string', cod_ibge_m: 'string', slug: 'string' },
          descFields:   { nm_municip: 'Município', cod_ibge_m: 'Código IBGE' },
        },
      },
      {
        key: 'estados_ne',
        layer: {
          label: 'Limites Estaduais',
          meta: 'Fronteiras dos estados do Nordeste',
          url: VECTOR_TILES_URL,
          sourceLayer: 'estados_ne',
          zIndex: 35,
          active: true,
          noPopup: true,
        },
      },
    ],
  },

  // 2. IVS — Índice de Vulnerabilidade à Desertificação ─────────────────────
  {
    key: 'ivs',
    label: 'IVD — Vulnerabilidade à Desertificação',
    icon: 'bi-exclamation-triangle',
    layer: null,
    children: [
      {
        key: 'ivd_sab',
        layer: {
          label: 'IVD — Índice de Vulnerabilidade à Desertificação',
          meta: 'Síntese dos índices de qualidade do solo, vegetação, clima e manejo',
          url: VECTOR_TILES_URL,
          sourceLayer: 'ivd_sab',
          zIndex: 10,
          active: true,
          searchFields: ['ivd'],
          popUpFields:  ['ivd'],
          fieldTypes:   { ivd: 'number' },
          descFields:   { ivd: 'Índice de Vulnerabilidade à Desertificação' },
        },
      },
    ],
  },

  // 3. Índices de Qualidade → IQS / IQV / IQC / IQM ──────────────────────────
  {
    key: 'indices_qualidade',
    label: 'Índices de Qualidade',
    icon: 'bi-graph-up-arrow',
    layer: null,
    children: [

      // 3.1 IQS — Índice de Qualidade do Solo ───────────────────────────────
      {
        key: 'iqs_group',
        label: 'IQS — Qualidade do Solo',
        icon: 'bi-geo',
        layer: null,
        children: [
          {
            key: 'iqs',
            layer: {
              label: 'Índice de Qualidade do Solo (IQS)',
              meta: 'Síntese de declividade, geologia, textura e tipos de solo',
              url: VECTOR_TILES_URL,
              sourceLayer: 'iqs',
              zIndex: 11,
              active: false,
              searchFields: ['iqs'],
              popUpFields:  ['iqs'],
              fieldTypes:   { iqs: 'number' },
              descFields:   { iqs: 'Índice de Qualidade do Solo' },
            },
          },
          {
            key: 'iqs_escores',
            label: 'Escores de Qualidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'textura_escores_de_qualidade',
                layer: {
                  label: 'Textura do Solo',
                  meta: 'Escores de qualidade atribuídos à textura do solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'textura_escores_de_qualidade',
                  zIndex: 12,
                  active: false,
                  searchFields: ['dsc_textur', 'texescores'],
                  popUpFields:  ['dsc_textur', 'texescores'],
                  fieldTypes:   { dsc_textur: 'string', texescores: 'number' },
                  descFields:   { dsc_textur: 'Textura do Solo', texescores: 'Escore de Qualidade da Textura' },
                },
              },
              {
                key: 'tipos_de_solos_escores_de_qualidade',
                layer: {
                  label: 'Tipos de Solos',
                  meta: 'Escores de qualidade atribuídos aos tipos de solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'tipos_de_solos_escores_de_qualidade',
                  zIndex: 13,
                  active: false,
                  searchFields: ['dsc_compon', 'solescores'],
                  popUpFields:  ['dsc_compon', 'solescores'],
                  fieldTypes:   { dsc_compon: 'string', solescores: 'number' },
                  descFields:   { dsc_compon: 'Componente Pedológico', solescores: 'Escore de Qualidade do Tipo de Solo' },
                },
              },
              {
                key: 'declividade_escores_de_qualidade',
                layer: {
                  label: 'Declividade',
                  meta: 'Escores de qualidade atribuídos à declividade do terreno',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'declividade_escores_de_qualidade',
                  zIndex: 14,
                  active: false,
                  searchFields: ['decescores'],
                  popUpFields:  ['decescores'],
                  fieldTypes:   { decescores: 'number' },
                  descFields:   { decescores: 'Escore de Qualidade da Declividade' },
                },
              },
              {
                key: 'geologia_escores_de_qualidade',
                layer: {
                  label: 'Geologia',
                  meta: 'Escores de qualidade atribuídos às formações geológicas',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'geologia_escores_de_qualidade',
                  zIndex: 15,
                  active: false,
                  searchFields: ['geoescores'],
                  popUpFields:  ['geoescores'],
                  fieldTypes:   { geoescores: 'number' },
                  descFields:   { geoescores: 'Escore de Qualidade da Geologia' },
                },
              },
            ],
          },
        ],
      },

      // 3.2 IQV — Índice de Qualidade da Vegetação ──────────────────────────
      {
        key: 'iqv_group',
        label: 'IQV — Qualidade da Vegetação',
        icon: 'bi-tree',
        layer: null,
        children: [
          {
            key: 'iqv',
            layer: {
              label: 'Índice de Qualidade da Vegetação (IQV)',
              meta: 'Síntese de NDVI, carbono orgânico e suscetibilidade à erosão hídrica',
              url: VECTOR_TILES_URL,
              sourceLayer: 'iqv',
              zIndex: 16,
              active: false,
              searchFields: ['iqv'],
              popUpFields:  ['iqv'],
              fieldTypes:   { iqv: 'number' },
              descFields:   { iqv: 'Índice de Qualidade da Vegetação' },
            },
          },
          {
            key: 'iqv_escores',
            label: 'Escores de Qualidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'ndvi_escore_de_qualidade',
                layer: {
                  label: 'NDVI',
                  meta: 'Escores de qualidade atribuídos ao índice de vegetação NDVI',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'ndvi_escore_de_qualidade',
                  zIndex: 17,
                  active: false,
                  searchFields: ['ndviscores'],
                  popUpFields:  ['ndviscores'],
                  fieldTypes:   { ndviscores: 'number' },
                  descFields:   { ndviscores: 'Escore de Qualidade do NDVI' },
                },
              },
              {
                key: 'carbono_organico_escores_de_qualidade',
                layer: {
                  label: 'Carbono Orgânico',
                  meta: 'Escores de qualidade atribuídos ao teor de carbono orgânico do solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'carbono_organico_escores_de_qualidade',
                  zIndex: 18,
                  active: false,
                  searchFields: ['co_scores'],
                  popUpFields:  ['co_scores'],
                  fieldTypes:   { co_scores: 'number' },
                  descFields:   { co_scores: 'Escore de Qualidade do Carbono Orgânico' },
                },
              },
              {
                key: 'suscetibilidade_erosao_escore_de_qualidade',
                layer: {
                  label: 'Suscetibilidade à Erosão Hídrica',
                  meta: 'Escores de qualidade atribuídos à suscetibilidade dos solos à erosão hídrica',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'suscetibilidade_erosao_escore_de_qualidade',
                  zIndex: 19,
                  active: false,
                  searchFields: ['sucescores'],
                  popUpFields:  ['sucescores'],
                  fieldTypes:   { sucescores: 'number' },
                  descFields:   { sucescores: 'Escore de Qualidade da Suscetibilidade à Erosão' },
                },
              },
            ],
          },
        ],
      },

      // 3.3 IQC — Índice de Qualidade Climática ─────────────────────────────
      {
        key: 'iqc_group',
        label: 'IQC — Qualidade Climática',
        icon: 'bi-cloud-rain',
        layer: null,
        children: [
          {
            key: 'iqc',
            layer: {
              label: 'Índice de Qualidade Climática (IQC)',
              meta: 'Síntese de índice de aridez, precipitação e evapotranspiração',
              url: VECTOR_TILES_URL,
              sourceLayer: 'iqc',
              zIndex: 20,
              active: false,
              searchFields: ['iqcescores'],
              popUpFields:  ['iqcescores'],
              fieldTypes:   { iqcescores: 'number' },
              descFields:   { iqcescores: 'Índice de Qualidade Climática' },
            },
          },
          {
            key: 'iqc_escores',
            label: 'Escores de Qualidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'ia_escores_de_qualidade',
                layer: {
                  label: 'Índice de Aridez',
                  meta: 'Escores de qualidade atribuídos ao índice de aridez',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'ia_escores_de_qualidade',
                  zIndex: 21,
                  active: false,
                  searchFields: ['ia_escores'],
                  popUpFields:  ['ia_escores'],
                  fieldTypes:   { ia_escores: 'number' },
                  descFields:   { ia_escores: 'Escore de Qualidade do Índice de Aridez' },
                },
              },
              {
                key: 'precipitacao_escores_de_qualidade',
                layer: {
                  label: 'Precipitação',
                  meta: 'Escores de qualidade atribuídos à precipitação pluviométrica',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'precipitacao_escores_de_qualidade',
                  zIndex: 22,
                  active: false,
                  searchFields: ['pcpescores'],
                  popUpFields:  ['pcpescores'],
                  fieldTypes:   { pcpescores: 'number' },
                  descFields:   { pcpescores: 'Escore de Qualidade da Precipitação' },
                },
              },
              {
                key: 'eto_escores_de_qualidade',
                layer: {
                  label: 'Evapotranspiração (ETo)',
                  meta: 'Escores de qualidade atribuídos à evapotranspiração de referência',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'eto_escores_de_qualidade',
                  zIndex: 23,
                  active: false,
                  searchFields: ['etoescores'],
                  popUpFields:  ['etoescores'],
                  fieldTypes:   { etoescores: 'number' },
                  descFields:   { etoescores: 'Escore de Qualidade da Evapotranspiração' },
                },
              },
            ],
          },
        ],
      },

      // 3.4 IQM — Índice de Qualidade de Manejo ─────────────────────────────
      {
        key: 'iqm_group',
        label: 'IQM — Qualidade de Manejo',
        icon: 'bi-people',
        layer: null,
        children: [
          {
            key: 'iqm',
            layer: {
              label: 'Índice de Qualidade de Manejo (IQM)',
              meta: 'Síntese de pressão animal, focos de queimada, densidade demográfica rural e IDHM',
              url: VECTOR_TILES_URL,
              sourceLayer: 'iqm',
              zIndex: 24,
              active: false,
              searchFields: ['iqm'],
              popUpFields:  ['iqm'],
              fieldTypes:   { iqm: 'number' },
              descFields:   { iqm: 'Índice de Qualidade de Manejo' },
            },
          },
          {
            key: 'iqm_escores',
            label: 'Escores de Qualidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'pressao_animal_escores_de_qualidade',
                layer: {
                  label: 'Pressão Animal',
                  meta: 'Escores de qualidade atribuídos à pressão animal sobre o território',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'pressao_animal_escores_de_qualidade',
                  zIndex: 25,
                  active: false,
                  searchFields: ['paescores'],
                  popUpFields:  ['paescores'],
                  fieldTypes:   { paescores: 'number' },
                  descFields:   { paescores: 'Escore de Qualidade da Pressão Animal' },
                },
              },
              {
                key: 'focos_queimadas_escores_dequalidade',
                layer: {
                  label: 'Focos de Queimada',
                  meta: 'Escores de qualidade atribuídos à ocorrência de focos de queimada',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'focos_queimadas_escores_dequalidade',
                  zIndex: 26,
                  active: false,
                  searchFields: ['fqescores'],
                  popUpFields:  ['fqescores'],
                  fieldTypes:   { fqescores: 'number' },
                  descFields:   { fqescores: 'Escore de Qualidade dos Focos de Queimada' },
                },
              },
              {
                key: 'densidade_demografica_rural_escores_de_qualidade',
                layer: {
                  label: 'Densidade Demográfica Rural',
                  meta: 'Escores de qualidade atribuídos à densidade demográfica rural',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'densidade_demografica_rural_escores_de_qualidade',
                  zIndex: 27,
                  active: false,
                  searchFields: ['drescores'],
                  popUpFields:  ['drescores'],
                  fieldTypes:   { drescores: 'number' },
                  descFields:   { drescores: 'Escore de Qualidade da Densidade Demográfica Rural' },
                },
              },
              {
                key: 'idhm_escores_de_qualidade',
                layer: {
                  label: 'IDHM',
                  meta: 'Escores de qualidade atribuídos ao Índice de Desenvolvimento Humano Municipal',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'idhm_escores_de_qualidade',
                  zIndex: 28,
                  active: false,
                  searchFields: ['idhmescore'],
                  popUpFields:  ['idhmescore'],
                  fieldTypes:   { idhmescore: 'number' },
                  descFields:   { idhmescore: 'Escore de Qualidade do IDHM' },
                },
              },
            ],
          },
        ],
      },
    ],
  },
]

// ─── OVERLAY_LAYERS PLANO (retrocompatibilidade com mapStore / MapContainer) ──
//
// Gerado automaticamente a partir de OVERLAY_TREE (percorrido recursivamente)
// para que MapContainer.vue não precise saber nada sobre hierarquia — ele só
// enxerga a lista plana de camadas, igual antes. Nunca editar diretamente.
//
function collectLayers(nodes, acc = {}) {
  for (const node of nodes) {
    if (node.layer) acc[node.key] = node.layer
    if (node.children) collectLayers(node.children, acc)
  }
  return acc
}

export const OVERLAY_LAYERS = collectLayers(OVERLAY_TREE)
