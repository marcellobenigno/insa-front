<script setup>
import logoLockup from '@/assets/logo-lockup-fine.svg'
import HeroCarousel from '@/components/HeroCarousel.vue'

const features = [
  {
    icon: 'bi-layers',
    title: 'Camadas temáticas',
    text: 'Mais de 20 camadas georreferenciadas cruzam dados de solo, vegetação, clima e manejo do território.'
  },
  {
    icon: 'bi-graph-up-arrow',
    title: 'Índices de Vulnerabilidade',
    text: 'Índices de vulnerabilidade do solo, vegetação, clima e manejo — sintetizados no Índice de Vulnerabilidade à Desertificação (IVD).'
  },
  {
    icon: 'bi-building',
    title: 'Apoio a políticas públicas',
    text: 'Dados técnicos para orientar o combate à desertificação e a recuperação de áreas degradadas.'
  }
]
</script>

<template>
  <div class="inicio-view">
    <section class="hero">
      <HeroCarousel />

      <div class="hero-inner">
        <div class="hero-mark-wrap">
          <div class="hero-mark-glow" aria-hidden="true" />
          <h1 class="hero-mark-heading">
            <img :src="logoLockup" class="hero-mark" alt="DesertPB" />
          </h1>
        </div>

      </div>
    </section>

    <section class="hero-intro">
      <p class="hero-body">
        O <strong>DesertPB</strong> reúne, em um só lugar, o mapeamento da vulnerabilidade à desertificação no
        semiárido paraibano. Ao cruzar indicadores de solo, vegetação, clima e manejo do
        território, a plataforma aponta onde a degradação avança com mais intensidade — e
        serve de base técnica para as políticas públicas estaduais de combate à
        desertificação e de recuperação de áreas degradadas.
      </p>

      <div class="hero-ctas">
        <RouterLink to="/mapa" class="btn-cta btn-cta-primary">
          <i class="bi bi-map" aria-hidden="true" />
          Explorar o mapa
        </RouterLink>
        <RouterLink to="/dashboard" class="btn-cta btn-cta-ghost">
          <i class="bi bi-bar-chart-line" aria-hidden="true" />
          Ver dashboard
        </RouterLink>
      </div>
    </section>

    <section class="ivd-scale" aria-label="Escala do Índice de Vulnerabilidade à Desertificação">
      <div class="ivd-scale-accent" aria-hidden="true" />
      <p class="ivd-scale-caption">Índice de Vulnerabilidade à Desertificação (IVD)</p>
      <div class="ivd-scale-bar" role="img"
           aria-label="Escala de cores: verde (baixa) a vermelho (muito alta)" />
      <div class="ivd-scale-labels">
        <span>Baixa</span>
        <span>Moderada</span>
        <span>Alta</span>
        <span>Muito Alta</span>
      </div>
    </section>

    <section class="features">
      <article v-for="f in features" :key="f.title" class="feature-card">
        <i :class="['bi', f.icon]" aria-hidden="true" />
        <h2>{{ f.title }}</h2>
        <p>{{ f.text }}</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.inicio-view {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-app);
}

/* ── Hero ─────────────────────────────────────────────────────────────────── */
.hero {
  position: relative;
  display: flex;
  justify-content: center;
  padding: 72px 24px 88px;
  overflow: hidden;
}

.hero::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 140px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, var(--bg-app) 100%);
  pointer-events: none;
  z-index: 0;
}

.hero-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 720px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.hero-mark-wrap {
  position: relative;
  margin-bottom: 28px;
  animation: fade-up 0.6s var(--transition-curve) both;
}

/* Fundo discreto atrás do ícone+wordmark — sem forma/borda visível, só um
   degradê radial suave que escurece um pouco a foto ao redor da logo pra
   destacá-la, sem parecer um adesivo colado por cima (já tentado antes). */
.hero-mark-glow {
  position: absolute;
  inset: -20% -14%;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.22) 42%,
    rgba(0, 0, 0, 0) 72%
  );
  pointer-events: none;
  z-index: 0;
}

.hero-mark-heading {
  position: relative;
  z-index: 1;
  margin: 0;
  line-height: 0;
}

.hero-mark {
  width: 300px;
  height: auto;
  display: block;
}

.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.85);
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
  animation: fade-up 0.6s var(--transition-curve) 0.03s both;
}

.eyebrow-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}

.hero-lead {
  margin: 0;
  font-size: clamp(16px, 2.4vw, 19px);
  font-weight: 500;
  color: #ffffff;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.4);
  animation: fade-up 0.6s var(--transition-curve) 0.1s both;
}

/* ── Hero intro (fora da área do carrossel) ──────────────────────────────── */
.hero-intro {
  max-width: 620px;
  margin: 0 auto;
  padding: 40px 24px 0;
  text-align: center;
}

.hero-body {
  margin: 0 0 28px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-muted);
  animation: fade-up 0.6s var(--transition-curve) 0.15s both;
}

.hero-ctas {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  animation: fade-up 0.6s var(--transition-curve) 0.2s both;
}

.btn-cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 22px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: transform var(--transition-speed) var(--transition-curve),
  background var(--transition-speed) var(--transition-curve),
  box-shadow var(--transition-speed) var(--transition-curve);
}

.btn-cta:hover {
  transform: translateY(-1px);
}

.btn-cta-primary,
.btn-cta-ghost {
  background: #6b7280;
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
}

.btn-cta-primary:hover,
.btn-cta-ghost:hover {
  background: #575e68;
}

@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-mark-wrap,
  .hero-eyebrow,
  .hero-lead,
  .hero-body,
  .hero-ctas {
    animation: none;
  }
}

/* ── IVD scale (signature element) ───────────────────────────────────────── */
.ivd-scale {
  max-width: 620px;
  margin: 0 auto;
  padding: 48px 24px 50px;
  text-align: center;
}

.ivd-scale-accent {
  width: 36px;
  height: 3px;
  margin: 0 auto 18px;
  border-radius: 9999px;
  background: linear-gradient(90deg, #a6d96a 0%, #e8ffc0 34%, #fdae61 67%, #d7191c 100%);
}

.ivd-scale-caption {
  margin: 0 0 10px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--text-dim);
}

.ivd-scale-bar {
  height: 10px;
  border-radius: 9999px;
  background: linear-gradient(90deg, #a6d96a 0%, #e8ffc0 34%, #fdae61 67%, #d7191c 100%);
  box-shadow: var(--shadow-lg);
}

.ivd-scale-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

/* ── Feature cards ────────────────────────────────────────────────────────── */
.features {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px 72px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.feature-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 22px 20px;
  transition: transform var(--transition-speed) var(--transition-curve),
  background var(--transition-speed) var(--transition-curve);
}

.feature-card:hover {
  transform: translateY(-2px);
  background: var(--card-bg-hover);
}

.feature-card > .bi {
  font-size: 22px;
  color: var(--accent);
}

.feature-card h2 {
  margin: 12px 0 6px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-muted);
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 720px) {
  .hero {
    padding: 56px 20px 64px;
  }

  .ivd-scale {
    padding-top: 72px;
  }

  .features {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .hero-eyebrow {
    font-size: 11px;
    text-align: center;
  }

  .hero-ctas {
    gap: 8px;
  }
}
</style>
