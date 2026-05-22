// src/utils/mapPopup.js

/**
 * Gera o conteúdo HTML estruturado com múltiplas seções (uma para cada camada ativa).
 * Filtra chaves de identificação técnica (id, ID, gid).
 * @param {Array} layersData - Lista de objetos [{ label: '...', properties: {...} }]
 */
export function createPopupContent(layersData) {
  // Regex flexível para pegar variações de ID, id, gid, FID, fid, etc.
  const idPattern = /^(fid|id|gid|objectid)$/i;

  const sectionsHtml = layersData
    .map(layer => {
      const rows = Object.entries(layer.properties)
        // Filtra chaves de identificação técnica de forma insensível a maiúsculas/minúsculas
        .filter(([key]) => !idPattern.test(key))
        .map(([key, value]) => {
          const displayValue = value !== null && value !== undefined ? value : '-'
          return `
            <tr>
              <td class="gfi-key">${key}</td>
              <td class="gfi-val">${displayValue}</td>
            </tr>`
        })
        .join('')

      // Se a camada não tiver atributos visíveis após o filtro
      if (!rows) {
        return `
          <div class="gfi-section">
            <div class="gfi-title">${layer.label}</div>
            <div class="gfi-empty">Sem atributos visíveis</div>
          </div>`
      }

      // Estrutura puríssima, sem classes inline ou margins forçadas
      return `
        <div class="gfi-section">
          <div class="gfi-title">${layer.label}</div>
          <table class="gfi-table">
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>`
    })
    .join('') // Removemos a tag <hr> daqui! O CSS cuida das divisórias de forma limpa.

  return `<div class="gfi-popup">${sectionsHtml}</div>`
}