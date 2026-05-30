<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Chart, BarController, BarElement,
  CategoryScale, LinearScale, Tooltip,
} from 'chart.js'
import statsData from '@/assets/stats.json'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)

const props = defineProps({
  sourceLayer: { type: String, required: true },
  label:       { type: String, required: true },
})
const emit = defineEmits(['close'])

const canvasRef = ref(null)
let chartInstance = null

const entry   = computed(() => statsData[props.sourceLayer])
const classes = computed(() => entry.value?.classes ?? [])
const totalKm2 = computed(() => entry.value?.total_km2 ?? 0)

function formatLabel(label) {
  const trimmed = label.trim()
  if (!isNaN(Number(trimmed))) {
    return parseFloat(trimmed).toLocaleString('pt-BR', { maximumFractionDigits: 2 })
  }
  return label
}

function truncate(label, max = 18) {
  const s = formatLabel(label)
  return s.length > max ? s.slice(0, max - 1) + '…' : s
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function buildChart() {
  if (!canvasRef.value || classes.value.length === 0) return
  const gridColor = cssVar('--border-color') || 'rgba(128,128,128,0.2)'
  const tickColor = cssVar('--text-muted')   || '#94a3b8'

  chartInstance = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: classes.value.map(c => truncate(c.label)),
      datasets: [{
        data: classes.value.map(c => c.area_km2),
        backgroundColor: classes.value.map(c => c.color),
        borderColor:     classes.value.map(c => c.color),
        borderWidth: 1,
        borderRadius: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title:  (items) => formatLabel(classes.value[items[0].dataIndex].label),
            label:  (ctx)   => ' ' + ctx.parsed.y.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' km²',
          },
        },
      },
      scales: {
        y: {
          title: { display: true, text: 'Área (km²)', color: tickColor, font: { size: 11 } },
          grid:  { color: gridColor },
          ticks: { color: tickColor, font: { size: 11 } },
        },
        x: {
          grid:  { display: false },
          ticks: { color: tickColor, font: { size: 10 }, maxRotation: 40, minRotation: 0 },
        },
      },
    },
  })
}

function onKey(e) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  buildChart()
  document.addEventListener('keydown', onKey)
})

onUnmounted(() => {
  chartInstance?.destroy()
  document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div class="chart-backdrop" @click="emit('close')" />

    <!-- Modal -->
    <div class="chart-modal-wrap" role="dialog" aria-modal="true">
      <div class="chart-modal modal-lg">
        <!-- Header -->
        <div class="chart-header">
          <div>
            <div class="chart-title">{{ label }}</div>
          </div>
          <button class="chart-close" aria-label="Fechar" @click="emit('close')">
            <i class="bi bi-x-lg" />
          </button>
        </div>

        <!-- Gráfico -->
        <div class="chart-body">
          <div class="chart-canvas-wrap">
            <canvas ref="canvasRef" />
          </div>

          <!-- Legenda customizada -->
          <div class="chart-legend">
            <div
              v-for="c in classes"
              :key="c.label"
              class="legend-row"
            >
              <span class="legend-dot" :style="{ background: c.color }" />
              <span class="legend-label">{{ formatLabel(c.label) }}</span>
              <span class="legend-area">
                {{ c.area_km2.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) }} km²
              </span>
              <span class="legend-pct">
                ({{ (c.area_km2 / totalKm2 * 100).toFixed(1) }}%)
              </span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="chart-footer">
          <button class="btn btn-sm btn-secondary" @click="emit('close')">Fechar</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* ── Backdrop ────────────────────────────────────────────────────────────────── */
.chart-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1055;
}

/* ── Wrapper de posicionamento ───────────────────────────────────────────────── */
.chart-modal-wrap {
  position: fixed;
  inset: 0;
  z-index: 1056;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  pointer-events: none;
}

/* ── Modal ───────────────────────────────────────────────────────────────────── */
.chart-modal {
  pointer-events: all;
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  color: var(--text-main);
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────────────────────────────── */
.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px 20px 14px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.chart-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.3;
}

.chart-subtitle {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 3px;
}

.chart-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px 4px;
  font-size: 1rem;
  line-height: 1;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
  flex-shrink: 0;
  margin-left: 12px;
}

.chart-close:hover {
  color: var(--text-main);
  background: var(--btn-bg-hover);
}

/* ── Body ────────────────────────────────────────────────────────────────────── */
.chart-body {
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}

.chart-canvas-wrap {
  height: 300px;
  position: relative;
  margin-bottom: 20px;
}

/* ── Legenda ─────────────────────────────────────────────────────────────────── */
.chart-legend {
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 0.78rem;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.legend-area {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.legend-pct {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 52px;
  text-align: right;
}

/* ── Footer ──────────────────────────────────────────────────────────────────── */
.chart-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}
</style>
