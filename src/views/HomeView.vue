<script setup>
import MapContainer from '@/components/MapContainer.vue'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
</script>

<template>
  <div class="map-layout">
    <!-- Barra lateral com controles de camada -->
    <aside class="sidebar">

      <!-- Seção: Camadas de Sobreposição -->
      <p class="sidebar-title">
        <FontAwesomeIcon :icon="['fas', 'layer-group']" class="me-2" />
        Camadas de Sobreposição
      </p>
      <div class="d-flex flex-column gap-2 mb-4">
        <div
          v-for="layer in mapStore.availableOverlays"
          :key="layer.key"
          class="form-check"
        >
          <input
            :id="`overlay-${layer.key}`"
            class="form-check-input"
            type="checkbox"
            :checked="mapStore.visibleOverlays[layer.key]"
            @change="mapStore.toggleOverlay(layer.key)"
          />
          <label class="form-check-label" :for="`overlay-${layer.key}`">
            {{ layer.label }}
          </label>
        </div>
      </div>

      <hr class="sidebar-divider" />

      <!-- Seção: Camada Base -->
      <p class="sidebar-title">
        <FontAwesomeIcon :icon="['fas', 'satellite']" class="me-2" />
        Camadas Base
      </p>
      <div class="d-flex flex-column gap-2">
        <div
          v-for="layer in mapStore.availableBaseLayers"
          :key="layer.key"
          class="form-check"
        >
          <input
            :id="`base-${layer.key}`"
            class="form-check-input"
            type="radio"
            name="baseLayer"
            :value="layer.key"
            :checked="mapStore.activeBaseLayerKey === layer.key"
            @change="mapStore.setBaseLayer(layer.key)"
          />
          <label class="form-check-label" :for="`base-${layer.key}`">
            {{ layer.label }}
          </label>
        </div>
      </div>

    </aside>

    <!-- Área principal do mapa -->
    <main class="map-area">
      <MapContainer />
    </main>
  </div>
</template>

<style scoped>
.map-layout {
  display: flex;
  height: 100dvh;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  padding: 1.25rem 1rem;
  background-color: #f8f9fa;
  border-right: 1px solid #dee2e6;
  z-index: 1000;
  overflow-y: auto;
}

.sidebar-title {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c757d;
  margin-bottom: 0.75rem;
}

.sidebar-divider {
  border-color: #dee2e6;
  margin: 0 0 1rem;
}

.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}
</style>
