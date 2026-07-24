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
// exatamente a hierarquia do projeto (Semiárido → Índices de Vulnerabilidade →
// IVS/IVV/IVC/IVM → Escores de Vulnerabilidade → camada).
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
      {
        key: 'limite_do_semiarido_br',
        layer: {
          label: 'Limite do Semiárido BR',
          meta: 'Contorno da região do Semiárido Brasileiro',
          url: VECTOR_TILES_URL,
          sourceLayer: 'limite_do_semiarido_br',
          zIndex: 34,
          active: false,
          noPopup: true,
        },
      },
    ],
  },

  // 2. IVD — Índice de Vulnerabilidade à Desertificação ─────────────────────
  {
    key: 'ivd_group',
    label: 'IVD — Vulnerabilidade à Desertificação',
    icon: 'bi-exclamation-triangle',
    layer: null,
    children: [
      {
        key: 'ivd_sab',
        layer: {
          label: 'IVD — Índice de Vulnerabilidade à Desertificação',
          meta: 'Síntese dos índices de vulnerabilidade do solo, vegetação, clima e manejo',
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

  // 3. Índices de Vulnerabilidade → IVS / IVV / IVC / IVM ────────────────────
  {
    key: 'indices_vulnerabilidade',
    label: 'Índices de Vulnerabilidade',
    icon: 'bi-graph-up-arrow',
    layer: null,
    children: [

      // 3.1 IVS — Índice de Vulnerabilidade do Solo ─────────────────────────
      {
        key: 'ivs_group',
        label: 'IVS — Vulnerabilidade do Solo',
        icon: 'bi-geo',
        layer: null,
        children: [
          {
            key: 'ivs',
            layer: {
              label: 'Índice de Vulnerabilidade do Solo (IVS)',
              meta: 'Síntese de declividade, geologia, textura e tipos de solo',
              url: VECTOR_TILES_URL,
              sourceLayer: 'ivs',
              zIndex: 11,
              active: false,
              searchFields: ['ivs'],
              popUpFields:  ['ivs'],
              fieldTypes:   { ivs: 'number' },
              descFields:   { ivs: 'Índice de Vulnerabilidade do Solo' },
            },
          },
          {
            key: 'ivs_escores',
            label: 'Escores de Vulnerabilidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'textura_escores_de_vulnerabilidade',
                layer: {
                  label: 'Textura do Solo',
                  meta: 'Escores de vulnerabilidade atribuídos à textura do solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'textura_escores_de_vulnerabilidade',
                  zIndex: 12,
                  active: false,
                  searchFields: ['dsc_textur', 'texescores'],
                  popUpFields:  ['dsc_textur', 'texescores'],
                  fieldTypes:   { dsc_textur: 'string', texescores: 'number' },
                  descFields:   { dsc_textur: 'Textura do Solo', texescores: 'Escore de Vulnerabilidade da Textura' },
                },
              },
              {
                key: 'tipos_de_solos_escores_de_vulnerabilidade',
                layer: {
                  label: 'Tipos de Solos',
                  meta: 'Escores de vulnerabilidade atribuídos aos tipos de solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'tipos_de_solos_escores_de_vulnerabilidade',
                  zIndex: 13,
                  active: false,
                  searchFields: ['dsc_compon', 'solescores'],
                  popUpFields:  ['dsc_compon', 'solescores'],
                  fieldTypes:   { dsc_compon: 'string', solescores: 'number' },
                  descFields:   { dsc_compon: 'Componente Pedológico', solescores: 'Escore de Vulnerabilidade do Tipo de Solo' },
                },
              },
              {
                key: 'declividade_escores_de_vulnerabilidade',
                layer: {
                  label: 'Declividade',
                  meta: 'Escores de vulnerabilidade atribuídos à declividade do terreno',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'declividade_escores_de_vulnerabilidade',
                  zIndex: 14,
                  active: false,
                  searchFields: ['decescores'],
                  popUpFields:  ['decescores'],
                  fieldTypes:   { decescores: 'number' },
                  descFields:   { decescores: 'Escore de Vulnerabilidade da Declividade' },
                },
              },
              {
                key: 'geologia_escores_de_vulnerabilidade',
                layer: {
                  label: 'Geologia',
                  meta: 'Escores de vulnerabilidade atribuídos às formações geológicas',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'geologia_escores_de_vulnerabilidade',
                  zIndex: 15,
                  active: false,
                  searchFields: ['geoescores'],
                  popUpFields:  ['geoescores'],
                  fieldTypes:   { geoescores: 'number' },
                  descFields:   { geoescores: 'Escore de Vulnerabilidade da Geologia' },
                },
              },
            ],
          },
        ],
      },

      // 3.2 IVV — Índice de Vulnerabilidade da Vegetação ────────────────────
      {
        key: 'ivv_group',
        label: 'IVV — Vulnerabilidade da Vegetação',
        icon: 'bi-tree',
        layer: null,
        children: [
          {
            key: 'ivv',
            layer: {
              label: 'Índice de Vulnerabilidade da Vegetação (IVV)',
              meta: 'Síntese de NDVI, carbono orgânico e suscetibilidade à erosão hídrica',
              url: VECTOR_TILES_URL,
              sourceLayer: 'ivv',
              zIndex: 16,
              active: false,
              searchFields: ['ivv'],
              popUpFields:  ['ivv'],
              fieldTypes:   { ivv: 'number' },
              descFields:   { ivv: 'Índice de Vulnerabilidade da Vegetação' },
            },
          },
          {
            key: 'ivv_escores',
            label: 'Escores de Vulnerabilidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'ndvi_escore_de_vulnerabilidade',
                layer: {
                  label: 'NDVI',
                  meta: 'Escores de vulnerabilidade atribuídos ao índice de vegetação NDVI',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'ndvi_escore_de_vulnerabilidade',
                  zIndex: 17,
                  active: false,
                  searchFields: ['ndviscores'],
                  popUpFields:  ['ndviscores'],
                  fieldTypes:   { ndviscores: 'number' },
                  descFields:   { ndviscores: 'Escore de Vulnerabilidade do NDVI' },
                },
              },
              {
                key: 'carbono_organico_escores_de_vulnerabilidade',
                layer: {
                  label: 'Carbono Orgânico',
                  meta: 'Escores de vulnerabilidade atribuídos ao teor de carbono orgânico do solo',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'carbono_organico_escores_de_vulnerabilidade',
                  zIndex: 18,
                  active: false,
                  searchFields: ['co_scores'],
                  popUpFields:  ['co_scores'],
                  fieldTypes:   { co_scores: 'number' },
                  descFields:   { co_scores: 'Escore de Vulnerabilidade do Carbono Orgânico' },
                },
              },
              {
                key: 'suscetibilidade_erosao_escore_de_vulnerabilidade',
                layer: {
                  label: 'Suscetibilidade à Erosão Hídrica',
                  meta: 'Escores de vulnerabilidade atribuídos à suscetibilidade dos solos à erosão hídrica',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'suscetibilidade_erosao_escore_de_vulnerabilidade',
                  zIndex: 19,
                  active: false,
                  searchFields: ['sucescores'],
                  popUpFields:  ['sucescores'],
                  fieldTypes:   { sucescores: 'number' },
                  descFields:   { sucescores: 'Escore de Vulnerabilidade da Suscetibilidade à Erosão' },
                },
              },
            ],
          },
        ],
      },

      // 3.3 IVC — Índice de Vulnerabilidade Climática ───────────────────────
      {
        key: 'ivc_group',
        label: 'IVC — Vulnerabilidade Climática',
        icon: 'bi-cloud-rain',
        layer: null,
        children: [
          {
            key: 'ivc',
            layer: {
              label: 'Índice de Vulnerabilidade Climática (IVC)',
              meta: 'Síntese de índice de aridez, precipitação e evapotranspiração',
              url: VECTOR_TILES_URL,
              sourceLayer: 'ivc',
              zIndex: 20,
              active: false,
              searchFields: ['ivc'],
              popUpFields:  ['ivc'],
              fieldTypes:   { ivc: 'number' },
              descFields:   { ivc: 'Índice de Vulnerabilidade Climática' },
            },
          },
          {
            key: 'ivc_escores',
            label: 'Escores de Vulnerabilidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'ia_escores_de_vulnerabilidade',
                layer: {
                  label: 'Índice de Aridez',
                  meta: 'Escores de vulnerabilidade atribuídos ao índice de aridez',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'ia_escores_de_vulnerabilidade',
                  zIndex: 21,
                  active: false,
                  searchFields: ['ia_escores'],
                  popUpFields:  ['ia_escores'],
                  fieldTypes:   { ia_escores: 'number' },
                  descFields:   { ia_escores: 'Escore de Vulnerabilidade do Índice de Aridez' },
                },
              },
              {
                key: 'precipitacao_escores_de_vulnerabilidade',
                layer: {
                  label: 'Precipitação',
                  meta: 'Escores de vulnerabilidade atribuídos à precipitação pluviométrica',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'precipitacao_escores_de_vulnerabilidade',
                  zIndex: 22,
                  active: false,
                  searchFields: ['pcpescores'],
                  popUpFields:  ['pcpescores'],
                  fieldTypes:   { pcpescores: 'number' },
                  descFields:   { pcpescores: 'Escore de Vulnerabilidade da Precipitação' },
                },
              },
              {
                key: 'eto_escores_de_vulnerabilidade',
                layer: {
                  label: 'Evapotranspiração (ETo)',
                  meta: 'Escores de vulnerabilidade atribuídos à evapotranspiração de referência',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'eto_escores_de_vulnerabilidade',
                  zIndex: 23,
                  active: false,
                  searchFields: ['etoescores'],
                  popUpFields:  ['etoescores'],
                  fieldTypes:   { etoescores: 'number' },
                  descFields:   { etoescores: 'Escore de Vulnerabilidade da Evapotranspiração' },
                },
              },
            ],
          },
        ],
      },

      // 3.4 IVM — Índice de Vulnerabilidade de Manejo ───────────────────────
      {
        key: 'ivm_group',
        label: 'IVM — Vulnerabilidade de Manejo',
        icon: 'bi-people',
        layer: null,
        children: [
          {
            key: 'ivm',
            layer: {
              label: 'Índice de Vulnerabilidade de Manejo (IVM)',
              meta: 'Síntese de pressão animal, focos de queimada, densidade demográfica rural e IDHM',
              url: VECTOR_TILES_URL,
              sourceLayer: 'ivm',
              zIndex: 24,
              active: false,
              searchFields: ['ivm'],
              popUpFields:  ['ivm'],
              fieldTypes:   { ivm: 'number' },
              descFields:   { ivm: 'Índice de Vulnerabilidade de Manejo' },
            },
          },
          {
            key: 'ivm_escores',
            label: 'Escores de Vulnerabilidade',
            icon: 'bi-list-nested',
            layer: null,
            children: [
              {
                key: 'pressao_animal_escores_de_vulnerabilidade',
                layer: {
                  label: 'Pressão Animal',
                  meta: 'Escores de vulnerabilidade atribuídos à pressão animal sobre o território',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'pressao_animal_escores_de_vulnerabilidade',
                  zIndex: 25,
                  active: false,
                  searchFields: ['paescores'],
                  popUpFields:  ['paescores'],
                  fieldTypes:   { paescores: 'number' },
                  descFields:   { paescores: 'Escore de Vulnerabilidade da Pressão Animal' },
                },
              },
              {
                key: 'focos_queimadas_escores_de_vulnerabilidade',
                layer: {
                  label: 'Focos de Queimada',
                  meta: 'Escores de vulnerabilidade atribuídos à ocorrência de focos de queimada',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'focos_queimadas_escores_de_vulnerabilidade',
                  zIndex: 26,
                  active: false,
                  searchFields: ['fqescores'],
                  popUpFields:  ['fqescores'],
                  fieldTypes:   { fqescores: 'number' },
                  descFields:   { fqescores: 'Escore de Vulnerabilidade dos Focos de Queimada' },
                },
              },
              {
                key: 'densidade_demografica_rural_escores_de_vulnerabilidade',
                layer: {
                  label: 'Densidade Demográfica Rural',
                  meta: 'Escores de vulnerabilidade atribuídos à densidade demográfica rural',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'densidade_demografica_rural_escores_de_vulnerabilidade',
                  zIndex: 27,
                  active: false,
                  searchFields: ['drescores'],
                  popUpFields:  ['drescores'],
                  fieldTypes:   { drescores: 'number' },
                  descFields:   { drescores: 'Escore de Vulnerabilidade da Densidade Demográfica Rural' },
                },
              },
              {
                key: 'idhm_escores_de_vulnerabilidade',
                layer: {
                  label: 'IDHM',
                  meta: 'Escores de vulnerabilidade atribuídos ao Índice de Desenvolvimento Humano Municipal',
                  url: VECTOR_TILES_URL,
                  sourceLayer: 'idhm_escores_de_vulnerabilidade',
                  zIndex: 28,
                  active: false,
                  searchFields: ['idhmescore'],
                  popUpFields:  ['idhmescore'],
                  fieldTypes:   { idhmescore: 'number' },
                  descFields:   { idhmescore: 'Escore de Vulnerabilidade do IDHM' },
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
