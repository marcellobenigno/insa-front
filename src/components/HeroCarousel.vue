<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const slides = [
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/caatinga-serra-borborema.jpg`,
    alt: 'Vegetação seca da caatinga em primeiro plano, com as serras do planalto da Borborema ao fundo, sob céu azul com nuvens.',
    credit: 'IoannesCarolus / Wikimedia Commons, CC BY-SA 4.0',
  },
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/mandacaru-por-do-sol.jpg`,
    alt: 'Cacto mandacaru recortado contra a luz dourada do pôr do sol no sertão paraibano.',
    credit: 'lubasi / Wikimedia Commons, CC BY-SA 2.0',
  },
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/cajazeiras-vista-aerea.jpg`,
    alt: 'Vista aérea de drone da cidade de Cajazeiras, no sertão paraibano, com as serras secas ao fundo.',
    credit: 'Gonsarubesu / Wikimedia Commons, CC BY-SA 4.0',
  },
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/lajedo-granito-cactos.jpg`,
    alt: 'Afloramentos de granito arredondados entre cactos e vegetação da caatinga, com um pequeno açude ao fundo.',
    credit: 'Renalle Ruana Pessoa Ramos / Wikimedia Commons, CC BY-SA 3.0',
  },
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/trilha-caatinga-seca.jpg`,
    alt: 'Trilha de terra batida entre árvores sem folhas da caatinga, iluminada pela luz quente do fim de tarde.',
    credit: 'Zelma Brito / Wikimedia Commons, CC BY-SA 3.0',
  },
  {
    src: `${import.meta.env.BASE_URL}images/semiarido/arvore-seca-caatinga.jpg`,
    alt: 'Árvore sem folhas típica da caatinga, silhuetada contra um céu azul com nuvens, cercada por vegetação seca.',
    credit: 'IoannesCarolus / Wikimedia Commons, CC BY-SA 4.0',
  },
]

const current = ref(0)
const prefersReducedMotion =
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

let timer = null
const INTERVAL_MS = 6500

function goTo(index) {
  current.value = (index + slides.length) % slides.length
}

function next() {
  goTo(current.value + 1)
}

function prev() {
  goTo(current.value - 1)
}

function play() {
  if (prefersReducedMotion || timer) return
  timer = setInterval(next, INTERVAL_MS)
}

function pause() {
  clearInterval(timer)
  timer = null
}

function handleVisibility() {
  if (document.hidden) {
    pause()
  } else {
    play()
  }
}

onMounted(() => {
  play()
  document.addEventListener('visibilitychange', handleVisibility)
})

onBeforeUnmount(() => {
  pause()
  document.removeEventListener('visibilitychange', handleVisibility)
})
</script>

<template>
  <div
    class="hero-carousel"
    role="region"
    aria-roledescription="carrossel"
    aria-label="Fotos do semiárido paraibano"
    @mouseenter="pause"
    @mouseleave="play"
    @focusin="pause"
    @focusout="play"
  >
    <div class="carousel-track">
      <figure
        v-for="(slide, i) in slides"
        :key="slide.src"
        class="carousel-slide"
        :class="{ 'is-active': i === current }"
      >
        <img
          :src="slide.src"
          :alt="slide.alt"
          class="carousel-img"
          :loading="i === 0 ? 'eager' : 'lazy'"
          :fetchpriority="i === 0 ? 'high' : 'auto'"
        />
      </figure>
      <div class="carousel-scrim" />
    </div>

    <p class="carousel-credit">{{ slides[current].credit }}</p>

    <button type="button" class="carousel-arrow carousel-arrow-prev" aria-label="Foto anterior" @click="prev">
      <i class="bi bi-chevron-left" aria-hidden="true" />
    </button>
    <button type="button" class="carousel-arrow carousel-arrow-next" aria-label="Próxima foto" @click="next">
      <i class="bi bi-chevron-right" aria-hidden="true" />
    </button>

    <div class="carousel-dots">
      <button
        v-for="(slide, i) in slides"
        :key="slide.src"
        type="button"
        class="carousel-dot"
        :class="{ 'is-active': i === current }"
        :aria-label="`Ir para foto ${i + 1}`"
        :aria-current="i === current ? 'true' : undefined"
        @click="goTo(i)"
      />
    </div>
  </div>
</template>

<style scoped>
.hero-carousel {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  background: #000;
}

.carousel-track {
  position: absolute;
  inset: 0;
}

.carousel-slide {
  position: absolute;
  inset: 0;
  margin: 0;
  opacity: 0;
  transition: opacity 1.1s ease;
}

.carousel-slide.is-active {
  opacity: 1;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 8s linear;
  transform: scale(1);
}

.carousel-slide.is-active .carousel-img {
  transform: scale(1.08);
}

.carousel-scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.55) 0%,
    rgba(0, 0, 0, 0.42) 40%,
    rgba(0, 0, 0, 0.5) 75%,
    rgba(0, 0, 0, 0.65) 100%
  );
  pointer-events: none;
}

.carousel-credit {
  position: absolute;
  left: 16px;
  bottom: 12px;
  margin: 0;
  color: #ffffff;
  font-size: 11px;
  font-weight: 400;
  opacity: 0.65;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s;
}

.hero-carousel:hover .carousel-arrow {
  opacity: 1;
}

.carousel-arrow:hover {
  background: rgba(0, 0, 0, 0.5);
}

.carousel-arrow-prev {
  left: 16px;
}

.carousel-arrow-next {
  right: 16px;
}

.carousel-dots {
  position: absolute;
  right: 16px;
  bottom: 12px;
  display: flex;
  gap: 6px;
}

.carousel-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, transform 0.2s;
}

.carousel-dot.is-active {
  background: #ffffff;
  transform: scale(1.3);
}

@media (max-width: 720px) {
  .carousel-arrow {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .carousel-slide {
    transition: opacity 0.3s linear;
  }

  .carousel-img,
  .carousel-slide.is-active .carousel-img {
    transition: none;
    transform: none;
  }
}
</style>
