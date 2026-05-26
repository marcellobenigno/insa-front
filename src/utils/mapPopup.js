// src/utils/mapPopup.js

/**
 * Gera o conteúdo HTML estruturado com múltiplas seções (uma para cada camada ativa).
 *
 * @param {Array} layersData - Lista de objetos:
 *   {
 *     label:       string,               // Nome da camada (título da seção)
 *     properties:  Record<string, any>,  // Atributos brutos da feição
 *     popUpFields: string[] | undefined, // Campos a exibir (ordem respeitada); se ausente, exibe todos
 *     descFields:  Record<string, string> | undefined, // Rótulo amigável por campo; fallback = nome do campo
 *   }
 */
export function createPopupContent(layersData) {
  // Regex flexível para pular chaves de identificação técnica (id, gid, fid, objectid…)
  const idPattern = /^(fid|id|gid|objectid)$/i

  const sectionsHtml = layersData
    .map(layer => {
      const { properties, popUpFields, descFields = {} } = layer

      // Determina quais entradas exibir e em que ordem
      let entries
      if (popUpFields && popUpFields.length > 0) {
        // Usa a lista explícita, na ordem declarada, ignorando campos ausentes na feição
        entries = popUpFields
          .filter(key => Object.prototype.hasOwnProperty.call(properties, key))
          .map(key => [key, properties[key]])
      } else {
        // Fallback: todos os campos, exceto IDs técnicos
        entries = Object.entries(properties).filter(([key]) => !idPattern.test(key))
      }

      const rows = entries
        .map(([key, value]) => {
          const displayKey   = descFields[key] ?? key
          const displayValue = value !== null && value !== undefined ? value : '-'
          return `
            <tr>
              <td class="gfi-key">${displayKey}</td>
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
    .join('')

  return `<div class="gfi-popup">${sectionsHtml}</div>`
}
