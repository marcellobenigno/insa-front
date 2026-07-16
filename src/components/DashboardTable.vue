<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  municipios: { type: Array, required: true }, // [{ cod_ibge_m, nm_municip, value, class_label, class_color }]
  selected: { type: String, default: null }, // cod_ibge_m selecionado
})
const emit = defineEmits(['select'])

const PAGE_SIZE = 10

const sortDir = ref('desc')
const filterText = ref('')
const currentPage = ref(1)

function normalize(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

const rows = computed(() => {
  const q = normalize(filterText.value.trim())
  const filtered = q
    ? props.municipios.filter((m) => normalize(m.nm_municip).includes(q))
    : props.municipios
  return [...filtered].sort((a, b) =>
    sortDir.value === 'desc' ? b.value - a.value : a.value - b.value,
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(rows.value.length / PAGE_SIZE)))

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return rows.value.slice(start, start + PAGE_SIZE)
})

const rangeLabel = computed(() => {
  if (rows.value.length === 0) return 'Nenhum resultado'
  const start = (currentPage.value - 1) * PAGE_SIZE + 1
  const end = Math.min(currentPage.value * PAGE_SIZE, rows.value.length)
  return `${start}–${end} de ${rows.value.length}`
})

// Filtro/ordenação/troca de índice mudam o conjunto de resultados — sempre volta pra página 1.
watch([filterText, sortDir, () => props.municipios], () => {
  currentPage.value = 1
})

function toggleSort() {
  sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
}

function selectRow(m) {
  emit('select', props.selected === m.cod_ibge_m ? null : m.cod_ibge_m)
}

function clearFilter() {
  filterText.value = ''
  // Limpar o filtro também desfaz o destaque no mapa — não faz sentido manter
  // um município em zoom/realce que talvez nem apareça mais na lista.
  emit('select', null)
}

function goToPage(page) {
  currentPage.value = Math.min(Math.max(1, page), totalPages.value)
}
</script>

<template>
  <div class="dashboard-table">
    <div class="table-toolbar">
      <div class="table-search">
        <i class="bi bi-search" aria-hidden="true" />
        <input
          v-model="filterText"
          type="text"
          placeholder="Filtrar município..."
          aria-label="Filtrar município"
        />
        <button v-if="filterText" class="clear-btn" aria-label="Limpar filtro" @click="clearFilter">
          <i class="bi bi-x" aria-hidden="true" />
        </button>
      </div>
      <span class="table-count">{{ rows.length }} município{{ rows.length === 1 ? '' : 's' }}</span>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th class="col-rank">#</th>
            <th>Município</th>
            <th class="col-value sortable" @click="toggleSort">
              Valor médio
              <i
                class="bi"
                :class="sortDir === 'desc' ? 'bi-caret-down-fill' : 'bi-caret-up-fill'"
              />
            </th>
            <th>Classe dominante</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(m, i) in pagedRows"
            :key="m.cod_ibge_m"
            class="row-selectable"
            :class="{ 'is-selected': selected === m.cod_ibge_m }"
            @click="selectRow(m)"
          >
            <td class="col-rank">{{ (currentPage - 1) * PAGE_SIZE + i + 1 }}</td>
            <td>{{ m.nm_municip }}</td>
            <td class="col-value">
              {{ m.value.toLocaleString('pt-BR', { maximumFractionDigits: 3 }) }}
            </td>
            <td>
              <span class="badge-dot" :style="{ background: m.class_color ?? '#9ca3af' }" />
              {{ m.class_label ?? '—' }}
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td colspan="4" class="empty-row">Nenhum município encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="table-pagination">
      <span class="pagination-range">{{ rangeLabel }}</span>
      <div class="pagination-controls">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          aria-label="Página anterior"
          @click="goToPage(currentPage - 1)"
        >
          <i class="bi bi-chevron-left" aria-hidden="true" />
        </button>
        <span class="pagination-label">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          aria-label="Próxima página"
          @click="goToPage(currentPage + 1)"
        >
          <i class="bi bi-chevron-right" aria-hidden="true" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-table {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
}

.table-search {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 280px;
}

.table-search .bi-search {
  position: absolute;
  left: 12px;
  font-size: 12px;
  color: var(--text-dim);
  pointer-events: none;
}

.table-search input {
  width: 100%;
  padding: 7px 30px 7px 32px;
  background: var(--btn-bg);
  border: 1px solid var(--border-color);
  border-radius: 9999px;
  color: var(--text-main);
  font-size: 13px;
  outline: none;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.table-search input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--bg-accent-dim);
}

.clear-btn {
  position: absolute;
  right: 8px;
  border: none;
  background: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 2px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 13px;
}

.clear-btn:hover {
  color: var(--text-main);
}

.table-count {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.table-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.table-wrap::-webkit-scrollbar {
  width: 4px;
}
.table-wrap::-webkit-scrollbar-track {
  background: transparent;
}
.table-wrap::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead th {
  position: sticky;
  top: 0;
  background: var(--bg-sidebar);
  text-align: left;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-dim);
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

th.sortable {
  cursor: pointer;
  user-select: none;
}

th.sortable:hover {
  color: var(--text-main);
}

th.sortable .bi {
  font-size: 9px;
  margin-left: 2px;
}

.col-rank {
  width: 40px;
}
.col-value {
  width: 120px;
}

tbody td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-main);
  transition: background 0.12s;
}

tbody tr:last-child td {
  border-bottom: none;
}

.row-selectable {
  cursor: pointer;
}

.row-selectable:hover td {
  background: var(--btn-bg);
}

.row-selectable.is-selected td {
  background: var(--bg-accent-dim);
}

.row-selectable.is-selected td:first-child {
  border-left: 3px solid var(--accent);
}

.badge-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}

.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 20px;
}

/* ── Paginação ────────────────────────────────────────────────────────────────── */
.table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.pagination-range {
  font-size: 12px;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  min-width: 44px;
  text-align: center;
}

.page-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: var(--btn-bg);
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transition:
    background 0.15s,
    color 0.15s,
    border-color 0.15s;
}

.page-btn:hover:not(:disabled) {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: default;
}
</style>
