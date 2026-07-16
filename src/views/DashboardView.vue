<script setup>
import { ref, computed, watch } from 'vue'
import dashboardData from '@/assets/dashboard_stats.json'
import { OVERLAY_LAYERS } from '@/config/layers'
import { getThematicColor } from '@/utils/mapRenderer'
import DashboardMiniMap from '@/components/DashboardMiniMap.vue'
import DashboardChart from '@/components/DashboardChart.vue'
import DashboardPieChart from '@/components/DashboardPieChart.vue'
import DashboardTable from '@/components/DashboardTable.vue'

// IVD (vulnerabilidade à desertificação) é o índice síntese de maior destaque
// no INSA — vem primeiro no seletor e já carrega selecionado ao abrir o dashboard.
const INDEX_DISPLAY_ORDER = ['ivd_sab', 'iqs', 'iqv', 'iqc', 'iqm']

const indexOptions = INDEX_DISPLAY_ORDER.filter((key) => dashboardData.indices_meta[key]).map(
  (key) => ({
    key,
    label:
      OVERLAY_LAYERS[key]?.descFields?.[dashboardData.indices_meta[key].field_used] ??
      key.toUpperCase(),
  }),
)

const selectedIndex = ref(indexOptions[0].key)
const selectedMunicipio = ref(null) // cod_ibge_m

const municipiosList = computed(() => {
  const fieldUsed = dashboardData.indices_meta[selectedIndex.value].field_used
  return Object.values(dashboardData.municipios)
    .map((m) => {
      const indexData = m.indices[selectedIndex.value]
      return {
        cod_ibge_m: m.cod_ibge_m,
        nm_municip: m.nm_municip,
        slug: m.slug,
        ...indexData,
        // Cor da classe dominante por ÁREA (class_color, acima) é diferente de
        // "qual classe o valor médio pertence" — num ranking ordenado por valor,
        // colorir pela classe da área faz municípios com valores quase idênticos
        // (perto de uma fronteira de classe) mostrarem cores inconsistentes com
        // a ordem do gráfico. valueColor classifica o próprio valor plotado,
        // com a mesma lógica usada no mapa (getThematicColor/styles.json).
        valueColor:
          indexData.value !== null
            ? getThematicColor(selectedIndex.value, { [fieldUsed]: indexData.value })
            : null,
      }
    })
    .filter((m) => m.value !== null)
})

// Trocar de índice não deve manter um destaque de um contexto diferente na tabela.
watch(selectedIndex, () => {
  selectedMunicipio.value = null
})
</script>

<template>
  <div class="dashboard-view">
    <header class="dashboard-header">
      <div>
        <h1>Comparativo entre Municípios</h1>
        <p class="dashboard-subtitle">
          Cruzamento dos índices de qualidade com os
          {{ Object.keys(dashboardData.municipios).length }}
          municípios do Semiárido da PB
        </p>
      </div>
      <label class="index-select-wrap">
        <span class="index-select-label">Índice</span>
        <select v-model="selectedIndex" class="index-select" aria-label="Selecionar índice">
          <option v-for="opt in indexOptions" :key="opt.key" :value="opt.key">
            {{ opt.label }}
          </option>
        </select>
      </label>
    </header>

    <section class="dashboard-section">
      <h2 class="section-eyebrow">Explorar municípios</h2>
      <div class="dashboard-grid grid-explore">
        <section class="dashboard-panel">
          <h3 class="panel-title">
            <i class="bi bi-geo-alt-fill" aria-hidden="true" />Distribuição espacial
          </h3>
          <div class="panel-body">
            <DashboardMiniMap
              :source-layer="selectedIndex"
              :selected-municipio="selectedMunicipio"
              @clear-selection="selectedMunicipio = null"
            />
          </div>
        </section>

        <section class="dashboard-panel">
          <h3 class="panel-title">
            <i class="bi bi-table" aria-hidden="true" />Todos os municípios
          </h3>
          <div class="panel-body">
            <DashboardTable
              :municipios="municipiosList"
              :selected="selectedMunicipio"
              @select="selectedMunicipio = $event"
            />
          </div>
        </section>
      </div>
    </section>

    <section class="dashboard-section">
      <h2 class="section-eyebrow">Análise do índice selecionado</h2>
      <div class="dashboard-grid grid-charts">
        <section class="dashboard-panel">
          <h3 class="panel-title">
            <i class="bi bi-pie-chart-fill" aria-hidden="true" />Distribuição por classe
          </h3>
          <div class="panel-body">
            <DashboardPieChart :source-layer="selectedIndex" />
          </div>
        </section>

        <section class="dashboard-panel">
          <h3 class="panel-title">
            <i class="bi bi-bar-chart-line-fill" aria-hidden="true" />Ranking dos municípios
          </h3>
          <div class="panel-body">
            <DashboardChart :municipios="municipiosList" />
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard-view {
  height: 100%;
  overflow-y: auto;
  padding: 28px 32px 44px;
  background: var(--bg-app);
}

.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 23px;
  font-weight: 600;
  letter-spacing: -0.4px;
  color: var(--text-main);
  margin: 0 0 4px;
}

.dashboard-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.index-select-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.index-select-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-dim);
  padding-left: 2px;
}

.index-select {
  padding: 9px 16px;
  border-radius: 9999px;
  border: 1px solid var(--border-color);
  background: var(--btn-bg);
  color: var(--text-main);
  font-size: 13px;
  font-weight: 500;
  outline: none;
  cursor: pointer;
  min-width: 280px;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}

.index-select:hover {
  border-color: var(--accent);
}

.index-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--bg-accent-dim);
}

/* ── Seções ──────────────────────────────────────────────────────────────────── */
.dashboard-section {
  margin-bottom: 32px;
}

.dashboard-section:last-child {
  margin-bottom: 0;
}

.section-eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin: 0 0 14px;
  padding-left: 2px;
}

/* ── Grid ────────────────────────────────────────────────────────────────────── */
.dashboard-grid {
  display: grid;
  gap: 20px;
  align-items: stretch;
}

.grid-charts {
  grid-template-columns: minmax(300px, 0.85fr) minmax(360px, 1.15fr);
}

.grid-explore {
  grid-template-columns: minmax(320px, 1fr) minmax(380px, 1.1fr);
}

/* ── Painel ──────────────────────────────────────────────────────────────────── */
.dashboard-panel {
  display: flex;
  flex-direction: column;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  padding: 20px 22px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease;
}

.dashboard-panel:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--text-main);
  margin: 0 0 16px;
  flex-shrink: 0;
}

.panel-title .bi {
  font-size: 13px;
  color: var(--accent);
}

.panel-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.grid-charts .dashboard-panel {
  min-height: 400px;
}

.grid-explore .dashboard-panel {
  min-height: 460px;
}

@media (max-width: 960px) {
  .grid-charts,
  .grid-explore {
    grid-template-columns: 1fr;
  }

  .grid-charts .dashboard-panel,
  .grid-explore .dashboard-panel {
    min-height: unset;
  }
}

@media (max-width: 640px) {
  .dashboard-view {
    padding: 20px 16px 32px;
  }

  .dashboard-header {
    flex-direction: column;
  }

  .index-select,
  .index-select-wrap {
    width: 100%;
    min-width: 0;
  }
}
</style>
