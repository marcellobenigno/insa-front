<script setup>
const team = [
  {
    name: 'Ricardo da Cunha Correia Lima',
    role: 'Engenheiro Eletricista, Doutor em Recursos Naturais',
    tag: 'Coordenador do projeto',
  },
  {
    name: 'Daiana Caroline Refati',
    role: 'Geógrafa, Mestre em Desenvolvimento Rural Sustentável',
  },
  {
    name: 'Jéssica Sousa Dantas',
    role: 'Engenheira Agrícola e Ambiental, Doutoranda em Meteorologia',
  },
  {
    name: 'Marcello Benigno Borges de Barros Filho',
    role: 'Engenheiro Civil, Mestre em Ciências Geodésicas e Tecnologias da Geoinformação',
  },
  {
    name: 'Mariana da Silva de Siqueira',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
  },
  {
    name: 'Santana Lívia de Lima',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
  },
  {
    name: 'Welinágila Grangeiro de Sousa',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
  },
]

function initials(name) {
  const parts = name.split(' ').filter(Boolean)
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}
</script>

<template>
  <div class="sobre-view">
    <section class="sobre-hero">
      <p class="sobre-eyebrow">DesertPB</p>
      <h1>Sobre</h1>
    </section>

    <section class="sobre-content">
      <p>
        O <strong>DesertPB</strong> é um WEBGIS fruto do projeto de pesquisa intitulado
        “Monitoramento com a utilização de ferramentas digitais, na mitigação do processo de
        desertificação com uso de palma forrageira no estado da Paraíba”, objeto da Emenda
        Parlamentar Individual nº 27140008/2024. Desenvolvido pelo Instituto Nacional do
        Semiárido, unidade de pesquisa do Ministério da Ciência, Tecnologia e Inovação, o sistema
        permite verificar o estado de vulnerabilidade à desertificação na região semiárida
        paraibana, através de índices de vulnerabilidade do solo, vegetação, clima e manejo da
        terra, calculados por uma série de indicadores ambientais e socioeconômicos.
      </p>

      <div class="sobre-tags">
        <span class="sobre-tag">
          <i class="bi bi-file-earmark-text" aria-hidden="true" />
          Emenda Parlamentar Individual nº 27140008/2024
        </span>
        <span class="sobre-tag">
          <i class="bi bi-building" aria-hidden="true" />
          Instituto Nacional do Semiárido (INSA)
        </span>
        <span class="sobre-tag">
          <i class="bi bi-bank" aria-hidden="true" />
          Ministério da Ciência, Tecnologia e Inovação
        </span>
      </div>
    </section>

    <section class="team-section">
      <h2>Equipe de desenvolvimento</h2>

      <div class="team-grid">
        <article v-for="member in team" :key="member.name" class="team-card">
          <span class="team-avatar" aria-hidden="true">{{ initials(member.name) }}</span>
          <div class="team-info">
            <h3>{{ member.name }}</h3>
            <p>{{ member.role }}</p>
            <span v-if="member.tag" class="team-tag">{{ member.tag }}</span>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.sobre-view {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-app);
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.sobre-hero {
  max-width: 680px;
  margin: 0 auto;
  padding: 56px 24px 8px;
  text-align: center;
}

.sobre-eyebrow {
  margin: 0 0 10px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
}

.sobre-hero h1 {
  margin: 0;
  font-size: clamp(30px, 5vw, 40px);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-main);
}

/* ── Institutional text ──────────────────────────────────────────────────── */
.sobre-content {
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 24px 8px;
}

.sobre-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text-muted);
  text-align: left;
}

.sobre-content strong {
  color: var(--text-main);
}

.sobre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}

.sobre-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 9999px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.sobre-tag .bi {
  color: var(--accent);
  font-size: 13px;
}

/* ── Team ─────────────────────────────────────────────────────────────────── */
.team-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px 72px;
}

.team-section h2 {
  margin: 0 0 20px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--text-dim);
  text-align: center;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.team-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  transition: transform var(--transition-speed) var(--transition-curve),
    background var(--transition-speed) var(--transition-curve);
}

.team-card:hover {
  transform: translateY(-2px);
  background: var(--card-bg-hover);
}

.team-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--bg-accent-dim);
  color: var(--accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.team-info h3 {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.3;
}

.team-info p {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.5;
  color: var(--text-muted);
}

.team-tag {
  display: inline-block;
  margin-top: 8px;
  padding: 2px 9px;
  border-radius: 9999px;
  background: var(--accent);
  color: var(--text-on-accent);
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
}
</style>
