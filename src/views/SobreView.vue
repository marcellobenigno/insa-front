<script setup>
import logoLockup from '@/assets/logo-lockup-fine.svg'
import AppFooter from '@/components/AppFooter.vue'

// Link do relatório final do projeto — vazio enquanto o relatório não é
// publicado. Com a string vazia, os links apontam pra "#", não navegam e o
// botão exibe "em breve"; basta preencher a URL quando ele estiver pronto.
const REPORT_URL = ''

const team = [
  {
    name: 'Ricardo da Cunha Correia Lima',
    role: 'Engenheiro Eletricista, Doutor em Recursos Naturais',
    tag: 'Coordenador do projeto',
    lattes: 'http://lattes.cnpq.br/1991607303660971',
  },
  {
    name: 'Daiana Caroline Refati',
    role: 'Geógrafa, Mestre em Desenvolvimento Rural Sustentável',
    lattes: 'http://lattes.cnpq.br/0151271333652553',
  },
  {
    name: 'Jéssica Sousa Dantas',
    role: 'Engenheira Agrícola e Ambiental, Doutoranda em Meteorologia',
    lattes: 'http://lattes.cnpq.br/5017616908612303',
  },
  {
    name: 'Marcello Benigno Borges de Barros Filho',
    role: 'Engenheiro Civil, Mestre em Ciências Geodésicas e Tecnologias da Geoinformação',
    lattes: 'http://lattes.cnpq.br/9018602479662912',
  },
  {
    name: 'Mariana da Silva de Siqueira',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
    lattes: 'http://lattes.cnpq.br/0754929803491263',
  },
  {
    name: 'Santana Lívia de Lima',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
    lattes: 'http://lattes.cnpq.br/9724080345845333',
  },
  {
    name: 'Welinágila Grangeiro de Sousa',
    role: 'Engenheira de Biossistemas, Doutora em Meteorologia',
    lattes: 'http://lattes.cnpq.br/7521514754114151',
  },
]

function initials(name) {
  const parts = name.split(' ').filter(Boolean)
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

const coordinator = team.find((member) => member.tag)
const members = team.filter((member) => !member.tag)
</script>

<template>
  <div class="sobre-view">
    <main class="sobre-main">
      <section class="sobre-hero">
        <img :src="logoLockup" class="sobre-mark" alt="DesertPB" />
        <h1>Sobre</h1>
      </section>

      <section class="sobre-content sobre-intro">
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
          <a
            href="https://www.gov.br/insa/pt-br"
            target="_blank"
            rel="noopener noreferrer"
            class="sobre-tag"
          >
            <i class="bi bi-building" aria-hidden="true" />
            Instituto Nacional do Semiárido (INSA)
          </a>
          <a
            href="https://www.gov.br/mcti/pt-br"
            target="_blank"
            rel="noopener noreferrer"
            class="sobre-tag"
          >
            <i class="bi bi-bank" aria-hidden="true" />
            Ministério da Ciência, Tecnologia e Inovação
          </a>
        </div>
      </section>

      <section class="sobre-content sobre-report">
        <h2 class="sobre-section-title">Relatório do projeto</h2>
        <p>
          O
          <a
            :href="REPORT_URL || '#'"
            :target="REPORT_URL ? '_blank' : undefined"
            rel="noopener noreferrer"
            class="report-inline-link"
            @click="!REPORT_URL && $event.preventDefault()"
            >Relatório do Projeto</a
          >
          descreve toda a metodologia utilizada para cálculo dos índices e indicadores de
          vulnerabilidade à desertificação, bem como uma análise dos resultados encontrados e um
          breve histórico das ações de PD&amp;I do Instituto Nacional do Semiárido relacionadas ao
          tema de combate à desertificação e recuperação de áreas degradadas.
        </p>

        <div class="sobre-tags">
          <a
            :href="REPORT_URL || '#'"
            :target="REPORT_URL ? '_blank' : undefined"
            rel="noopener noreferrer"
            class="sobre-tag"
            :aria-disabled="!REPORT_URL || undefined"
            @click="!REPORT_URL && $event.preventDefault()"
          >
            <i class="bi bi-file-earmark-text" aria-hidden="true" />
            Acessar relatório
            <span v-if="!REPORT_URL" class="report-soon">em breve</span>
          </a>
        </div>
      </section>

      <section class="team-section">
        <h2 class="sobre-section-title">Equipe de desenvolvimento</h2>

        <div class="team-lead-wrap">
          <article class="team-card team-lead">
            <span class="team-avatar" aria-hidden="true">{{ initials(coordinator.name) }}</span>
            <div class="team-info">
              <h3>
                <a
                  :href="coordinator.lattes"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="team-name-link"
                >
                  {{ coordinator.name }}
                </a>
              </h3>
              <p>{{ coordinator.role }}</p>
              <span class="team-tag">{{ coordinator.tag }}</span>
            </div>
          </article>
        </div>

        <div class="team-grid">
          <article v-for="member in members" :key="member.name" class="team-card">
            <span class="team-avatar" aria-hidden="true">{{ initials(member.name) }}</span>
            <div class="team-info">
              <h3>
                <a
                  :href="member.lattes"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="team-name-link"
                >
                  {{ member.name }}
                </a>
              </h3>
              <p>{{ member.role }}</p>
            </div>
          </article>
        </div>
      </section>
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.sobre-view {
  /* Uma única coluna e um único ritmo vertical pra todas as seções — antes
     texto (680px) e equipe (900px) tinham larguras e espaçamentos próprios,
     e as bordas das seções não alinhavam entre si. */
  --sobre-col: 760px;
  --sobre-gap: 56px;
  height: 100%;
  overflow-y: auto;
  background: var(--bg-app);
  /* Sticky footer — ver .inicio-view em InicioView.vue. */
  display: flex;
  flex-direction: column;
}

.sobre-main {
  flex: 1 0 auto;
}

.sobre-hero,
.sobre-content,
.team-section {
  max-width: var(--sobre-col);
  margin: 0 auto;
  padding-left: 24px;
  padding-right: 24px;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.sobre-hero {
  padding-top: 56px;
  padding-bottom: 0;
  text-align: center;
}

.sobre-mark {
  width: 190px;
  height: auto;
  margin-bottom: 18px;
  animation: sobre-fade-up 0.6s var(--transition-curve) both;
}

.sobre-hero h1 {
  margin: 0;
  font-size: clamp(30px, 5vw, 40px);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-main);
  animation: sobre-fade-up 0.6s var(--transition-curve) 0.05s both;
}

@keyframes sobre-fade-up {
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
  .sobre-mark,
  .sobre-hero h1 {
    animation: none;
  }
}

/* ── Institutional text ──────────────────────────────────────────────────── */
.sobre-content {
  padding-top: 40px;
  padding-bottom: 0;
}

.sobre-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text-muted);
  /* Justificado com hifenização (lang="pt-BR" no index.html) — sem
     hyphens, a coluna estreita no celular abre "rios" de espaço entre
     palavras longas como "desertificação"/"socioeconômicos". */
  text-align: justify;
  hyphens: auto;
  text-wrap: pretty;
}

/* Parágrafo de abertura um degrau acima do texto corrido — é a única
   seção sem título próprio, então o tamanho é o que marca a entrada. */
.sobre-intro p {
  font-size: 16px;
}

/* Título de seção — compartilhado por "Relatório do projeto" e "Equipe de
   desenvolvimento". Mantém o rótulo centralizado em caixa alta de antes,
   agora entre dois filetes (cor de borda do tema) que marcam a quebra de
   seção, e com --text-muted em vez de --text-dim: no tema escuro o
   --text-dim (#636366) tinha pouco contraste sobre o fundo. */
.sobre-section-title {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 0 0 24px;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  text-align: center;
}

.sobre-section-title::before,
.sobre-section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.sobre-content strong {
  color: var(--text-main);
}

.sobre-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
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
  text-decoration: none;
  transition:
    transform var(--transition-speed) var(--transition-curve),
    background var(--transition-speed) var(--transition-curve),
    color var(--transition-speed) var(--transition-curve);
}

.sobre-tag:hover {
  transform: translateY(-1px);
  background: var(--card-bg-hover);
  color: var(--text-main);
}

.sobre-tag .bi {
  color: var(--accent);
  font-size: 13px;
}

/* ── Report ───────────────────────────────────────────────────────────────── */
.sobre-report {
  padding-top: var(--sobre-gap);
}

.report-inline-link {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}

.report-inline-link:hover {
  text-decoration: underline;
}

.report-soon {
  padding: 1px 7px;
  border-radius: 9999px;
  background: var(--bg-accent-dim);
  color: var(--accent);
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* ── Team ─────────────────────────────────────────────────────────────────── */
.team-section {
  padding-top: var(--sobre-gap);
  padding-bottom: 80px;
}

.team-lead-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 14px;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.team-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 14px;
}

/* Coordenador — card único acima da grade, ocupando a mesma largura das
   duas colunas abaixo; mesmo background/borda dos demais, só com layout
   vertical e conteúdo centralizado. */
.team-lead {
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 24px 28px 22px;
  text-align: center;
}

.team-lead .team-avatar {
  width: 56px;
  height: 56px;
  margin-bottom: 6px;
  font-size: 16px;
}

.team-lead .team-tag {
  margin-top: 10px;
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
  margin: 0 0 3px;
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

/* Nome do participante linka pro Currículo Lattes — único efeito de hover
   nos cards da equipe (o card em si e o avatar não reagem a hover). */
.team-name-link {
  color: inherit;
  text-decoration: none;
  transition: color var(--transition-speed) var(--transition-curve);
}

.team-name-link:hover {
  color: var(--accent);
  text-decoration: underline;
}

/* ── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .sobre-view {
    --sobre-gap: 44px;
  }

  .sobre-hero {
    padding-top: 40px;
  }

  .sobre-mark {
    width: 160px;
  }

  .team-grid {
    grid-template-columns: 1fr;
  }
}
</style>
