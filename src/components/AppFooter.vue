<script setup>
const year = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <a
        href="https://www.gov.br/insa/pt-br"
        target="_blank"
        rel="noopener noreferrer"
        class="footer-brand"
      >
        <span class="footer-emblem" aria-hidden="true" />
        <span class="footer-name">Instituto Nacional do Semiárido</span>
      </a>
      <p class="footer-copy">© {{ year }} INSA · Todos os direitos reservados.</p>
    </div>
  </footer>
</template>

<style scoped>
/* Mesmo fundo/borda do AppNavbar — o rodapé fecha a página com o mesmo
   "material" do cabeçalho. */
.app-footer {
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-top: 1px solid var(--border-color);
}

.footer-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px 24px;
  flex-wrap: wrap;
}

.footer-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--text-main);
  text-decoration: none;
}

/* Emblema do INSA como máscara (PNG branco com alpha, recortado do logo
   oficial) pintada com a cor do texto — acompanha o tema claro/escuro
   sem precisar de duas versões do arquivo. */
.footer-emblem {
  width: 36px;
  height: 40px;
  flex-shrink: 0;
  background: currentColor;
  -webkit-mask: url('@/assets/insa-emblem.png') center / contain no-repeat;
  mask: url('@/assets/insa-emblem.png') center / contain no-repeat;
  transition: color var(--transition-speed) var(--transition-curve);
}

.footer-name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
  transition: color var(--transition-speed) var(--transition-curve);
}

.footer-brand:hover .footer-name,
.footer-brand:hover .footer-emblem {
  color: var(--accent);
}

.footer-copy {
  margin: 0;
  font-size: 12.5px;
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .footer-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
