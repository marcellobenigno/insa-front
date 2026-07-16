<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } from 'chart.js'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)

const props = defineProps({
  municipios: { type: Array, required: true }, // [{ nm_municip, value, valueColor }]
})

const RANK_SIZE = 15

const canvasRef = ref(null)
const mode = ref('top') // 'top' | 'bottom'
let chartInstance = null

// Ordenado do maior para o menor valor — o slice do topo dá os "15 mais",
// o slice da cauda (já na mesma ordem decrescente) dá os "15 menos".
const sorted = computed(() => [...props.municipios].sort((a, b) => b.value - a.value))

const displayed = computed(() =>
  mode.value === 'top' ? sorted.value.slice(0, RANK_SIZE) : sorted.value.slice(-RANK_SIZE),
)

const canvasHeight = computed(() => Math.max(280, displayed.value.length * 20))

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function buildChart() {
  if (!canvasRef.value || displayed.value.length === 0) return
  const gridColor = cssVar('--border-color') || 'rgba(128,128,128,0.2)'
  const tickColor = cssVar('--text-muted') || '#94a3b8'

  chartInstance = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: displayed.value.map((m) => m.nm_municip),
      datasets: [
        {
          data: displayed.value.map((m) => m.value),
          backgroundColor: displayed.value.map((m) => m.valueColor ?? '#9ca3af'),
          borderColor: displayed.value.map((m) => m.valueColor ?? '#9ca3af'),
          borderWidth: 1,
          borderRadius: 3,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              ' ' + ctx.parsed.x.toLocaleString('pt-BR', { maximumFractionDigits: 3 }),
          },
        },
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: tickColor, font: { size: 11 } },
        },
        y: {
          grid: { display: false },
          ticks: { color: tickColor, font: { size: 11 } },
        },
      },
    },
  })
}

function rebuildChart() {
  chartInstance?.destroy()
  buildChart()
}

watch(displayed, rebuildChart)
onMounted(buildChart)
onUnmounted(() => chartInstance?.destroy())
</script>

<template>
  <div class="dashboard-chart">
    <div class="chart-toolbar">
      <span class="chart-hint">
        {{
          mode === 'top'
            ? '15 municípios com maior valor médio'
            : '15 municípios com menor valor médio'
        }}
      </span>
      <div class="mode-toggle" role="group" aria-label="Selecionar os 15 mais ou os 15 menos">
        <button class="mode-btn" :class="{ 'is-active': mode === 'top' }" @click="mode = 'top'">
          15 mais
        </button>
        <button
          class="mode-btn"
          :class="{ 'is-active': mode === 'bottom' }"
          @click="mode = 'bottom'"
        >
          15 menos
        </button>
      </div>
    </div>
    <div class="chart-canvas-wrap" :style="{ minHeight: canvasHeight + 'px' }">
      <canvas ref="canvasRef" />
    </div>
  </div>
</template>

<style scoped>
.dashboard-chart {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

.chart-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.chart-hint {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mode-toggle {
  display: flex;
  padding: 3px;
  border-radius: 9999px;
  background: var(--btn-bg);
  border: 1px solid var(--border-color);
  flex-shrink: 0;
}

.mode-btn {
  padding: 5px 12px;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
}

.mode-btn:hover:not(.is-active) {
  color: var(--text-main);
}

.mode-btn.is-active {
  background: var(--accent);
  color: #ffffff;
}

.chart-canvas-wrap {
  position: relative;
  flex: 1;
  max-height: 70vh;
  overflow-y: auto;
}
</style>
