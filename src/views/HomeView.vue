<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
import MapContainer from '@/components/MapContainer.vue'
</script>

<template>
  <div class="home-view">
    <AppSidebar />
    <main class="map-area">
      <MapContainer />
    </main>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  width: 100%;
  height: 100%;
}

.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--bg-app);
}
</style>
