<script setup>
import AppNavbar from '@/components/AppNavbar.vue'
</script>

<template>
  <div class="app-shell">
    <AppNavbar />
    <div class="app-body">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.app-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
