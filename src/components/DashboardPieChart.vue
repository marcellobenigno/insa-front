<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Chart, PieController, ArcElement, Tooltip } from 'chart.js'
import statsData from '@/assets/stats.json'

Chart.register(PieController, ArcElement, Tooltip)

const props = defineProps({
  sourceLayer: { type: String, required: true },
})

const canvasRef = ref(null)
let chartInstance = null

const entry = computed(() => statsData[props.sourceLayer])
const classes = computed(() => entry.value?.classes ?? [])
const totalKm2 = computed(() => entry.value?.total_km2 ?? 0)

function formatLabel(label) {
  const trimmed = label.trim()
  if (!isNaN(Number(trimmed))) {
    return parseFloat(trimmed).toLocaleString('pt-BR', { maximumFractionDigits: 2 })
  }
  return label
}

function pct(areaKm2) {
  return ((areaKm2 / totalKm2.value) * 100).toFixed(1)
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function buildChart() {
  if (!canvasRef.value || classes.value.length === 0) return
  const borderColor = cssVar('--bg-sidebar') || '#ffffff'

  chartInstance = new Chart(canvasRef.value, {
    type: 'pie',
    data: {
      labels: classes.value.map((c) => formatLabel(c.label)),
      datasets: [
        {
          data: classes.value.map((c) => c.area_km2),
          backgroundColor: classes.value.map((c) => c.color),
          borderColor,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) =>
              ` ${ctx.label}: ${ctx.parsed.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} km² (${pct(ctx.parsed)}%)`,
          },
        },
      },
    },
  })
}

function rebuildChart() {
  chartInstance?.destroy()
  buildChart()
}

watch(() => props.sourceLayer, rebuildChart)
onMounted(buildChart)
onUnmounted(() => chartInstance?.destroy())
</script>

<template>
  <div class="dashboard-pie-chart">
    <div class="pie-canvas-wrap">
      <canvas ref="canvasRef" />
    </div>
    <div class="pie-legend">
      <div v-for="c in classes" :key="c.label" class="legend-row">
        <span class="legend-bar" :style="{ width: pct(c.area_km2) + '%', background: c.color }" />
        <span class="legend-dot" :style="{ background: c.color }" />
        <span class="legend-label">{{ formatLabel(c.label) }}</span>
        <span class="legend-pct">{{ pct(c.area_km2) }}%</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-pie-chart {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

.pie-canvas-wrap {
  position: relative;
  flex: 1;
  min-height: 180px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.legend-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 6px;
  border-radius: 6px;
  overflow: hidden;
}

.legend-bar {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  z-index: 0;
}

.legend-dot {
  position: relative;
  z-index: 1;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  position: relative;
  z-index: 1;
  flex: 1;
  font-size: 12px;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.legend-pct {
  position: relative;
  z-index: 1;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  flex-shrink: 0;
}
</style>
