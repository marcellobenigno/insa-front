<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useSidebar } from '@/composables/useSidebar'

const STORAGE_KEY = 'insa-tour-completed'
const SPOTLIGHT_PADDING = 8
const TOOLTIP_WIDTH = 320

const { isCollapsed, openBase, openCategories, toggleSidebar, toggleBase, toggleCategory } =
  useSidebar()

function ensureSidebarOpen() {
  if (isCollapsed.value) toggleSidebar()
}

// ── Passos do tour (reais, apontando para elementos existentes no app) ──────
const steps = ref([
  {
    target: null,
    title: 'Conheça o WebGIS do Semiárido PB',
    text: 'Esta ferramenta tem como objetivo apoiar o monitoramento da desertificação e da degradação das terras no Semiárido Paraibano. Aqui você visualiza o mapeamento produzido pelo INSA das áreas desertificadas e em processo de desertificação no estado da Paraíba. Use as setas abaixo para explorar os recursos disponíveis.',
  },
  {
    target: '.sidebar-collapse-btn',
    title: 'Exibir/ocultar painel de camadas',
    text: 'Este botão, sempre no topo do painel lateral, abre e fecha o painel, liberando mais espaço para o mapa quando você não precisa consultar as camadas.',
    beforeShow: () => {
      ensureSidebarOpen()
    },
  },
  {
    target: '#sidebar',
    title: 'Painel de Camadas',
    text: 'É por aqui que você acessa todo o acervo de camadas temáticas do WebGIS — desde os limites municipais até os índices de qualidade do semiárido paraibano. Cada camada pode ser ativada, combinada com outras e personalizada individualmente.',
    placement: 'right',
    beforeShow: () => {
      ensureSidebarOpen()
    },
  },
  {
    target: '[aria-controls="base-layers-content"]',
    title: 'Mapa de Fundo',
    text: 'Escolha o contexto visual que melhor se adapta à sua análise: imagem de satélite para identificar feições no campo, mapa com a malha viária para referências urbanas, ou relevo para entender a topografia da região.',
    beforeShow: () => {
      ensureSidebarOpen()
      if (!openBase.value) toggleBase()
    },
  },
  {
    target: '.layer-search-box',
    title: 'Busca Rápida de Camadas',
    text: 'Com dezenas de camadas disponíveis, use este campo para localizar rapidamente o dado que você precisa — basta digitar parte do nome, como "solos" ou "ndvi".',
    beforeShow: () => {
      ensureSidebarOpen()
    },
  },
  {
    target: ['#cat-block-semiarido_pb', '#cat-block-ivs', '#cat-block-indices_qualidade'],
    title: 'Camadas do Semiárido PB',
    text: 'Aqui estão os dados territoriais do Semiárido Paraibano: limites do semiárido, municípios e os índices integrados de qualidade — IQS, IQV, IQC e IQM. Ative mais de uma camada ao mesmo tempo para cruzar planos de informações.',
    beforeShow: () => {
      ensureSidebarOpen()
      if (!openCategories.semiarido_pb) toggleCategory('semiarido_pb')
      if (!openCategories.ivs) toggleCategory('ivs')
      if (!openCategories.indices_qualidade) toggleCategory('indices_qualidade')
    },
  },
  {
    target: '#cat-content-ivs .layer-actions',
    title: 'Ferramentas de Cada Camada',
    text: 'Com uma camada ativa, você tem à disposição: legenda de classes, busca por município ou atributo específico, controle de opacidade para sobrepor camadas com clareza, e um gráfico com a distribuição de área por classe.',
    beforeShow: () => {
      ensureSidebarOpen()
      if (!openCategories.ivs) toggleCategory('ivs')
    },
  },
  {
    target: '.clear-overlays-btn',
    title: 'Recomeçar a Visualização',
    text: 'Ativou muitas camadas e quer começar do zero? Este botão desliga todas de uma só vez, sem precisar desativar uma a uma.',
    beforeShow: () => {
      ensureSidebarOpen()
    },
  },
  {
    target: '.gs-footer',
    title: 'Localizar no Mapa',
    text: 'Informe o nome de um município, um endereço ou coordenadas geográficas para navegar diretamente até o ponto de interesse — ideal para trabalhos de campo ou análises por localidade.',
    beforeShow: () => {
      ensureSidebarOpen()
    },
  },
  {
    target: '.coord-display',
    title: 'Coordenadas sob o Cursor',
    text: 'Ao mover o mouse sobre o mapa, as coordenadas do ponto são exibidas aqui em tempo real — tanto em graus decimais quanto em graus, minutos e segundos. Útil para registrar localizações com precisão.',
    placement: 'top',
  },
])

// ── Estado do tour ────────────────────────────────────────────────────────
const visible = ref(false)
const currentStepIndex = ref(0)
const targetRect = ref(null)
const placement = ref('bottom')
let targetEls = []
let cleanupFns = []

const currentStep = computed(() => steps.value[currentStepIndex.value] ?? steps.value[0])
const isLastStep = computed(() => currentStepIndex.value === steps.value.length - 1)

// ── Localização e medição do elemento alvo ───────────────────────────────────
function isVisibleEl(el) {
  if (!el) return false
  const r = el.getBoundingClientRect()
  return r.width > 0 && r.height > 0 && el.offsetParent !== null
}

function waitForElement(selector, { timeout = 3000, interval = 50 } = {}) {
  return new Promise((resolve, reject) => {
    const start = performance.now()
    const poll = () => {
      const el = document.querySelector(selector)
      if (isVisibleEl(el)) return resolve(el)
      if (performance.now() - start >= timeout) {
        reject(new Error(`WebGisTour: elemento "${selector}" não apareceu a tempo.`))
        return
      }
      setTimeout(poll, interval)
    }
    poll()
  })
}

// Aceita um seletor único ou uma lista — várias seções destacadas de uma vez,
// combinadas depois em um único retângulo delimitador (measureTarget).
function waitForElements(target, options) {
  const selectors = Array.isArray(target) ? target : [target]
  return Promise.all(selectors.map((selector) => waitForElement(selector, options)))
}

function computePlacement(rect) {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const TOOLTIP_H = 220
  const GAP = 16
  const space = { bottom: vh - rect.bottom, top: rect.top, right: vw - rect.right, left: rect.left }
  const preferred = currentStep.value.placement ?? 'bottom'
  const order = [preferred, 'bottom', 'top', 'right', 'left']
  for (const p of order) {
    if (p === 'bottom' && space.bottom >= TOOLTIP_H + GAP) return 'bottom'
    if (p === 'top' && space.top >= TOOLTIP_H + GAP) return 'top'
    if (p === 'right' && space.right >= TOOLTIP_WIDTH + GAP) return 'right'
    if (p === 'left' && space.left >= TOOLTIP_WIDTH + GAP) return 'left'
  }
  return 'bottom'
}

function measureTarget() {
  if (!targetEls.length) {
    targetRect.value = null
    return
  }
  const rects = targetEls.map((el) => el.getBoundingClientRect())
  const top = Math.min(...rects.map((r) => r.top))
  const left = Math.min(...rects.map((r) => r.left))
  const right = Math.max(...rects.map((r) => r.right))
  const bottom = Math.max(...rects.map((r) => r.bottom))
  const merged = { top, left, right, bottom, width: right - left, height: bottom - top }
  targetRect.value = {
    top: merged.top,
    left: merged.left,
    width: merged.width,
    height: merged.height,
  }
  placement.value = computePlacement(merged)
}

function attachReactiveListeners() {
  const recompute = () => measureTarget()
  window.addEventListener('resize', recompute)
  window.addEventListener('scroll', recompute, true)

  const ro = new ResizeObserver(recompute)
  ro.observe(document.body)
  const sidebarEl = document.getElementById('sidebar')
  if (sidebarEl) ro.observe(sidebarEl)
  targetEls.forEach((el) => ro.observe(el))

  cleanupFns.push(() => {
    window.removeEventListener('resize', recompute)
    window.removeEventListener('scroll', recompute, true)
    ro.disconnect()
  })
}

function cleanupListeners() {
  cleanupFns.forEach((fn) => fn())
  cleanupFns = []
}

// ── Navegação ─────────────────────────────────────────────────────────────
async function goToStep(index) {
  cleanupListeners()

  if (index < 0) return
  if (index >= steps.value.length) {
    finishTour()
    return
  }

  currentStepIndex.value = index
  const step = steps.value[index]

  if (typeof step.beforeShow === 'function') {
    try {
      step.beforeShow()
    } catch (e) {
      console.warn('[WebGisTour] beforeShow falhou:', e)
    }
    await nextTick()
  }

  if (!step.target) {
    targetEls = []
    targetRect.value = null
    return
  }

  try {
    const els = await waitForElements(step.target)
    targetEls = els
    els[0].scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' })
    await new Promise((resolve) => setTimeout(resolve, 350))
    measureTarget()
    attachReactiveListeners()
  } catch (err) {
    console.warn(err.message)
    goToStep(index + 1)
  }
}

function startTour() {
  visible.value = true
  goToStep(0)
}

function nextStep() {
  goToStep(currentStepIndex.value + 1)
}
function prevStep() {
  goToStep(currentStepIndex.value - 1)
}

function persistCompleted() {
  try {
    localStorage.setItem(STORAGE_KEY, '1')
  } catch {
    /* localStorage indisponível */
  }
}

function skipTour() {
  cleanupListeners()
  visible.value = false
  persistCompleted()
}

function finishTour() {
  cleanupListeners()
  visible.value = false
  persistCompleted()
}

onMounted(() => {
  let alreadySeen = true
  try {
    alreadySeen = !!localStorage.getItem(STORAGE_KEY)
  } catch {
    /* localStorage indisponível */
  }
  if (!alreadySeen) setTimeout(startTour, 800)
})

onUnmounted(cleanupListeners)

// ── Estilos computados ───────────────────────────────────────────────────────
const spotlightStyle = computed(() => {
  if (!targetRect.value) return {}
  const { top, left, width, height } = targetRect.value
  return {
    top: `${top - SPOTLIGHT_PADDING}px`,
    left: `${left - SPOTLIGHT_PADDING}px`,
    width: `${width + SPOTLIGHT_PADDING * 2}px`,
    height: `${height + SPOTLIGHT_PADDING * 2}px`,
  }
})

const blockerStyle = computed(() => ({
  background: targetRect.value ? 'transparent' : 'rgba(0, 0, 0, 0.45)',
}))

const tooltipStyle = computed(() => {
  if (!targetRect.value) return {}
  const GAP = 14
  const { top, left, width, height } = targetRect.value
  const vw = window.innerWidth
  const vh = window.innerHeight
  let styleTop
  let styleLeft
  switch (placement.value) {
    case 'top':
      styleTop = top - GAP
      styleLeft = left + width / 2
      break
    case 'right':
      styleTop = top + height / 2
      styleLeft = left + width + GAP
      break
    case 'left':
      styleTop = top + height / 2
      styleLeft = left - GAP
      break
    default:
      styleTop = top + height + GAP
      styleLeft = left + width / 2
  }
  const clampedLeft = Math.min(
    Math.max(styleLeft, TOOLTIP_WIDTH / 2 + 12),
    vw - TOOLTIP_WIDTH / 2 - 12,
  )
  const clampedTop = Math.min(Math.max(styleTop, 12), vh - 12)
  return { top: `${clampedTop}px`, left: `${clampedLeft}px` }
})

defineExpose({ startTour })
</script>

<template>
  <button
    class="tour-trigger-btn"
    title="Ver tour guiado"
    aria-label="Iniciar tour guiado do WebGIS"
    @click.stop.prevent="startTour"
  >
    <i class="bi bi-question-circle" aria-hidden="true" />
  </button>

  <Teleport to="body">
    <div v-if="visible" class="tour-root">
      <div class="tour-blocker" :style="blockerStyle" @click.stop.prevent />

      <div
        v-if="targetRect"
        :key="currentStepIndex"
        class="tour-spotlight"
        :style="spotlightStyle"
      />

      <div
        class="tour-tooltip"
        :class="[`tour-tooltip--${targetRect ? placement : 'center'}`]"
        :style="tooltipStyle"
        role="dialog"
        aria-modal="true"
        :aria-label="currentStep.title"
        @click.stop.prevent
      >
        <div class="tour-tooltip-header">
          <span class="tour-step-count">{{ currentStepIndex + 1 }} / {{ steps.length }}</span>
          <button class="tour-close" aria-label="Pular tour" @click.stop.prevent="skipTour">
            <i class="bi bi-x-lg" aria-hidden="true" />
          </button>
        </div>

        <h3 class="tour-title">{{ currentStep.title }}</h3>
        <p class="tour-text">{{ currentStep.text }}</p>

        <div class="tour-dots" aria-hidden="true">
          <span
            v-for="(step, i) in steps"
            :key="i"
            class="tour-dot"
            :class="{ 'is-active': i === currentStepIndex }"
          />
        </div>

        <div class="tour-actions">
          <button
            v-if="currentStepIndex > 0"
            class="tour-btn tour-btn--ghost"
            @click.stop.prevent="prevStep"
          >
            Voltar
          </button>
          <button class="tour-btn tour-btn--ghost" @click.stop.prevent="skipTour">Pular</button>
          <button class="tour-btn tour-btn--primary" @click.stop.prevent="nextStep">
            {{ isLastStep ? 'Concluir' : 'Avançar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* ── Botão flutuante de ajuda ──────────────────────────────────────────────── */
.tour-trigger-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1000;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  color: #1d1d1f;
  font-size: 17px;
  cursor: pointer;
  box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
  transition:
    background 0.15s,
    color 0.15s,
    transform 0.1s;
}

[data-theme='dark'] .tour-trigger-btn {
  background: rgba(28, 28, 30, 0.85);
  color: #f5f5f7;
}

.tour-trigger-btn:hover {
  background: var(--accent);
  color: #ffffff;
}
.tour-trigger-btn:active {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  /* Evita colidir com o .sidebar-fab (top:12px right:12px em mobile) */
  .tour-trigger-btn {
    top: 64px;
  }
}

/* ── Overlay (blocker + spotlight), fora do fluxo via Teleport ────────────── */
.tour-root {
  position: fixed;
  inset: 0;
  z-index: 9999;
}

.tour-blocker {
  position: fixed;
  inset: 0;
  pointer-events: auto;
  transition: background 0.25s ease;
}

.tour-spotlight {
  position: fixed;
  border-radius: 12px;
  box-shadow:
    0 0 0 9999px rgba(0, 0, 0, 0.6),
    0 0 0 3px var(--accent),
    0 0 0 6px rgba(255, 255, 255, 0.25),
    0 0 24px 4px var(--accent);
  pointer-events: none;
  transition:
    top 0.3s ease,
    left 0.3s ease,
    width 0.3s ease,
    height 0.3s ease;
  animation:
    tour-spotlight-in 0.35s ease-out,
    tour-spotlight-pulse 1.8s ease-in-out 0.35s infinite;
}

@keyframes tour-spotlight-in {
  from {
    outline: 4px solid transparent;
    transform: scale(0.94);
    opacity: 0.4;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes tour-spotlight-pulse {
  0%,
  100% {
    box-shadow:
      0 0 0 9999px rgba(0, 0, 0, 0.6),
      0 0 0 3px var(--accent),
      0 0 0 6px rgba(255, 255, 255, 0.25),
      0 0 20px 2px var(--accent);
  }
  50% {
    box-shadow:
      0 0 0 9999px rgba(0, 0, 0, 0.6),
      0 0 0 4px var(--accent),
      0 0 0 8px rgba(255, 255, 255, 0.18),
      0 0 30px 8px var(--accent);
  }
}

@media (prefers-reduced-motion: reduce) {
  .tour-spotlight {
    animation: none;
  }
}

/* ── Tooltip ───────────────────────────────────────────────────────────────── */
.tour-tooltip {
  position: fixed;
  z-index: 10000;
  width: 320px;
  max-width: calc(100vw - 24px);
  padding: 20px;
  border-radius: 18px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border-color);
  box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
  color: var(--text-main);
  transition:
    top 0.3s ease,
    left 0.3s ease;
}

.tour-tooltip--bottom {
  transform: translate(-50%, 0);
}
.tour-tooltip--top {
  transform: translate(-50%, -100%);
}
.tour-tooltip--right {
  transform: translate(0, -50%);
}
.tour-tooltip--left {
  transform: translate(-100%, -50%);
}
.tour-tooltip--center {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* ── Seta apontando para o elemento em destaque ───────────────────────────── */
.tour-tooltip::after {
  content: '';
  position: absolute;
  width: 0;
  height: 0;
  border: 9px solid transparent;
}

.tour-tooltip--bottom::after {
  top: -17px;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: var(--bg-sidebar);
}

.tour-tooltip--top::after {
  bottom: -17px;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: var(--bg-sidebar);
}

.tour-tooltip--right::after {
  left: -17px;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: var(--bg-sidebar);
}

.tour-tooltip--left::after {
  right: -17px;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: var(--bg-sidebar);
}

.tour-tooltip--center::after {
  display: none;
}

.tour-tooltip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.tour-step-count {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-dim);
}

.tour-close {
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: var(--btn-bg);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition:
    background 0.15s,
    color 0.15s;
}

.tour-close:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}

.tour-title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.3px;
  margin: 0 0 6px;
}

.tour-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
  margin: 0 0 14px;
}

.tour-dots {
  display: flex;
  gap: 5px;
  margin-bottom: 16px;
}

.tour-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-color);
  transition: background 0.2s;
}

.tour-dot.is-active {
  background: var(--accent);
}

.tour-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.tour-btn {
  border: none;
  border-radius: 9999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.15s,
    transform 0.1s;
}

.tour-btn--ghost {
  background: var(--btn-bg);
  color: var(--text-muted);
}
.tour-btn--ghost:hover {
  background: var(--btn-bg-hover);
  color: var(--text-main);
}
.tour-btn--primary {
  background: var(--accent);
  color: var(--text-on-accent);
}
.tour-btn--primary:hover {
  background: var(--accent-hover);
}
.tour-btn:active {
  transform: scale(0.96);
}
</style>
