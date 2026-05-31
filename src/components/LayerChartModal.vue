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
          <button class="chart-close-btn" @click="emit('close')">Fechar</button>
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
  background: rgba(0, 0, 0, 0.4);
  z-index: 1055;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
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
  border-radius: 18px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
  color: var(--text-main);
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────────────────────────────── */
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.chart-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.374px;
  color: var(--text-main);
  line-height: 1.24;
}

.chart-close {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: var(--btn-bg);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  margin-left: 12px;
  transition: background 0.15s, color 0.15s, transform 0.1s;
}

.chart-close:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}

.chart-close:active {
  transform: scale(0.92);
}

/* ── Body ────────────────────────────────────────────────────────────────────── */
.chart-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.chart-canvas-wrap {
  height: 280px;
  position: relative;
  margin-bottom: 20px;
}

/* ── Legenda ─────────────────────────────────────────────────────────────────── */
.chart-legend {
  border-top: 1px solid var(--border-color);
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 13px;
  font-weight: 400;
  letter-spacing: -0.224px;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.legend-area {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.legend-pct {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 48px;
  text-align: right;
}

/* ── Footer ──────────────────────────────────────────────────────────────────── */
.chart-footer {
  padding: 14px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.chart-close-btn {
  padding: 8px 20px;
  border-radius: 9999px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, transform 0.1s;
}

.chart-close-btn:hover {
  background: var(--bg-accent-dim);
}

.chart-close-btn:active {
  transform: scale(0.97);
}
</style>
