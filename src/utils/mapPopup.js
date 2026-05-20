// src/utils/mapPopup.js

/**
 * Gera o conteúdo HTML estruturado com múltiplas seções (uma para cada camada ativa).
 * Filtra chaves de identificação técnica (id, ID, gid).
 * * @param {Array} layersData - Lista de objetos [{ label: '...', properties: {...} }]
 */
export function createPopupContent(layersData) {
  const ignoredKeys = ['fid', 'FID', 'Fid'];

  const sectionsHtml = layersData
    .map(layer => {
      const rows = Object.entries(layer.properties)
        // Filtra os campos ID, id e gid
        .filter(([key]) => !ignoredKeys.includes(key))
        .map(([key, value]) => {
          const displayValue = value !== null && value !== undefined ? value : '-'
          return `
            <tr>
              <td class="gfi-key">${key}</td>
              <td class="gfi-val">${displayValue}</td>
            </tr>`
        })
        .join('')

      // Se a camada não tiver atributos visíveis após o filtro, não renderiza a tabela
      if (!rows) {
        return `
          <div class="gfi-section">
            <div class="gfi-title">${layer.label}</div>
            <div style="font-size: 0.75rem; color: #9ca3af; padding: 4px 0;">Sem atributos visíveis</div>
          </div>`
      }

      return `
        <div class="gfi-section" style="margin-bottom: 12px;">
          <div class="gfi-title">${layer.label}</div>
          <table class="gfi-table">${rows}</table>
        </div>`
    })
    .join('<hr style="border: 0; border-top: 1px solid #374151; margin: 8px 0;" />')

  return `<div class="gfi-popup">${sectionsHtml}</div>`
}