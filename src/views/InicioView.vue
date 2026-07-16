<template>
  <div class="inicio-view">
    <i class="bi bi-cone-striped inicio-icon" aria-hidden="true" />
    <h1>Em construção</h1>
    <p>Esta página está em desenvolvimento. Enquanto isso, explore o mapa ou o dashboard.</p>
  </div>
</template>

<style scoped>
.inicio-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 24px;
  text-align: center;
  background: var(--bg-app);
}

.inicio-icon {
  font-size: 64px;
  color: var(--accent);
}

.inicio-view h1 {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.4px;
  color: var(--text-main);
  margin: 0;
}

.inicio-view p {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
  max-width: 360px;
}
</style>
