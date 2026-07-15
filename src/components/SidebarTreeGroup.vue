<script setup>
import { computed } from 'vue'
import { useSidebar } from '@/composables/useSidebar'
import LayerCard from './LayerCard.vue'

const props = defineProps({
  node:      { type: Object, required: true }, // nó de grupo enriquecido (store.availableTree)
  depth:     { type: Number, default: 0 },
  forceOpen: { type: Boolean, default: false }, // true durante busca por nome — força tudo expandido
})

const { isCollapsed, openCategories, toggleSidebar, toggleCategory } = useSidebar()

const isOpen = computed(() => props.forceOpen || !!openCategories[props.node.key])

function handleClick() {
  if (isCollapsed.value) {
    toggleSidebar()
    if (!openCategories[props.node.key]) toggleCategory(props.node.key)
  } else {
    toggleCategory(props.node.key)
  }
}

// Conta camadas visíveis/total em qualquer profundidade abaixo deste nó
function countLayers(node) {
  let total = 0
  let visible = 0
  for (const child of node.children ?? []) {
    if (child.layer) {
      total += 1
      if (child.layer.visible) visible += 1
    } else {
      const sub = countLayers(child)
      total += sub.total
      visible += sub.visible
    }
  }
  return { total, visible }
}

const counts = computed(() => countLayers(props.node))
</script>

<template>
  <section
    :id="`cat-block-${node.key}`"
    class="category-block"
    :class="{ 'is-open': isOpen, 'is-nested': depth > 0 }"
  >
    <button
      class="category-header btn-reset"
      :aria-expanded="isOpen"
      :aria-controls="`cat-content-${node.key}`"
      @click="handleClick"
    >
      <i class="bi cat-icon" :class="node.icon" aria-hidden="true" />
      <span class="cat-label" v-show="!isCollapsed">{{ node.label }}</span>

      <div class="cat-meta" v-show="!isCollapsed">
        <span v-if="counts.visible > 0" class="cat-badge me-1">{{ counts.visible }}</span>
        <span class="cat-count">{{ counts.total }}</span>
        <i class="bi bi-chevron-down cat-chevron ms-2" :class="{ 'is-rotated': isOpen }" />
      </div>
    </button>

    <div
      :id="`cat-content-${node.key}`"
      class="category-body"
      v-show="isOpen && !isCollapsed"
    >
      <div class="category-body-inner">
        <template v-for="child in node.children" :key="child.key">
          <LayerCard
            v-if="child.layer"
            type="overlay"
            :layer-key="child.key"
            :label="child.layer.label"
            :meta="child.layer.meta"
            :legend="child.layer.legend ?? null"
            :source-layer="child.layer.sourceLayer ?? ''"
            :search-fields="child.layer.searchFields ?? []"
            :field-types="child.layer.fieldTypes ?? {}"
            :desc-fields="child.layer.descFields ?? {}"
            :collapsed="isCollapsed"
          />
          <SidebarTreeGroup
            v-else
            :node="child"
            :depth="depth + 1"
            :force-open="forceOpen"
          />
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Indentação e leve redução de destaque para grupos aninhados (Índices de
   Qualidade > IQS > Escores de Qualidade), mantendo o visual base definido
   em src/assets/main.css (compartilhado com "Camadas Base" em AppSidebar.vue) */
.category-block.is-nested {
  margin: 8px 0 8px 12px;
  padding-left: 10px;
  border-left: 1px solid var(--border-color);
}

.category-block.is-nested .cat-label {
  font-size: 13.5px;
  font-weight: 600;
}

.category-block.is-nested .cat-icon {
  font-size: 14px;
  margin-right: 10px;
}

#sidebar.is-collapsed .category-block.is-nested {
  display: none;
}
</style>
