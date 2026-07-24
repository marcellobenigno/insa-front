<script setup>
import logoMark from '@/assets/logo-mark-fine.svg'

const features = [
  {
    icon: 'bi-layers',
    title: 'Camadas temáticas',
    text: 'Mais de 20 camadas georreferenciadas cruzam solo, vegetação, clima e manejo do território.',
  },
  {
    icon: 'bi-graph-up-arrow',
    title: 'Índices de vulnerabilidade',
    text: 'IVS, IVV, IVC e IVM sintetizados no Índice de Vulnerabilidade à Desertificação (IVD).',
  },
  {
    icon: 'bi-building',
    title: 'Apoio a políticas públicas',
    text: 'Dados técnicos para orientar o combate à desertificação e a recuperação de áreas degradadas.',
  },
]
</script>

<template>
  <div class="inicio-view">
    <section class="hero">
      <div class="hero-grid-bg" aria-hidden="true" />

      <div class="hero-inner">
        <img :src="logoMark" class="hero-mark" alt="" aria-hidden="true" />

        <p class="hero-eyebrow">
          Semiárido da Paraíba <span class="eyebrow-dot" aria-hidden="true" /> Monitoramento da
          Desertificação
        </p>

        <h1 class="hero-title">DesertPB</h1>

        <p class="hero-lead">
          Sistema de Informações Geográficas para a vulnerabilidade à desertificação
        </p>

        <p class="hero-body">
          O DesertPB reúne, em um só lugar, o mapeamento da vulnerabilidade à desertificação no
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

        <p class="hero-stats">
          <span><strong>198</strong> municípios monitorados</span>
          <span class="stats-sep" aria-hidden="true" />
          <span><strong>~52.590</strong> km² de semiárido mapeados</span>
        </p>
      </div>
    </section>

    <section class="ivd-scale" aria-label="Escala do Índice de Vulnerabilidade à Desertificação">
      <p class="ivd-scale-caption">Índice de Vulnerabilidade à Desertificação (IVD)</p>
      <div class="ivd-scale-bar" role="img" aria-label="Escala de cores: verde (baixa) a vermelho (muito alta)" />
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
  padding: 72px 24px 56px;
  overflow: hidden;
}

.hero-grid-bg {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, var(--border-color) 1px, transparent 1px);
  background-size: 26px 26px;
  opacity: 0.5;
  -webkit-mask-image: radial-gradient(ellipse 60% 55% at 50% 30%, #000 40%, transparent 100%);
  mask-image: radial-gradient(ellipse 60% 55% at 50% 30%, #000 40%, transparent 100%);
}

.hero-inner {
  position: relative;
  width: 100%;
  max-width: 720px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.hero-mark {
  width: 128px;
  height: auto;
  margin-bottom: 24px;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.12));
  animation: fade-up 0.6s var(--transition-curve) both;
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
  color: var(--text-muted);
  animation: fade-up 0.6s var(--transition-curve) 0.03s both;
}

.eyebrow-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}

.hero-title {
  margin: 0 0 14px;
  font-size: clamp(42px, 7vw, 64px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-main);
  animation: fade-up 0.6s var(--transition-curve) 0.05s both;
}

.hero-lead {
  margin: 0 0 18px;
  font-size: clamp(16px, 2.4vw, 19px);
  font-weight: 500;
  color: var(--text-main);
  opacity: 0.82;
  animation: fade-up 0.6s var(--transition-curve) 0.1s both;
}

.hero-body {
  margin: 0 0 32px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-muted);
  max-width: 620px;
  animation: fade-up 0.6s var(--transition-curve) 0.15s both;
}

.hero-ctas {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
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

.btn-cta-primary {
  background: var(--accent);
  color: var(--text-on-accent);
  box-shadow: 0 4px 14px var(--bg-accent-dim);
}

.btn-cta-primary:hover {
  background: var(--accent-hover);
}

.btn-cta-ghost {
  background: var(--card-bg);
  color: var(--text-main);
  border: 1px solid var(--border-color);
}

.btn-cta-ghost:hover {
  background: var(--card-bg-hover);
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 13px;
  color: var(--text-dim);
  animation: fade-up 0.6s var(--transition-curve) 0.25s both;
}

.hero-stats strong {
  color: var(--text-main);
  font-weight: 700;
}

.stats-sep {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--border-color);
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
  .hero-mark,
  .hero-eyebrow,
  .hero-title,
  .hero-lead,
  .hero-body,
  .hero-ctas,
  .hero-stats {
    animation: none;
  }
}

/* ── IVD scale (signature element) ───────────────────────────────────────── */
.ivd-scale {
  max-width: 620px;
  margin: 0 auto;
  padding: 0 24px 56px;
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
    padding: 56px 20px 40px;
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

  .hero-stats {
    flex-direction: column;
    gap: 4px;
  }

  .stats-sep {
    display: none;
  }
}
</style>
