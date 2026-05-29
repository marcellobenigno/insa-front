import { ref, reactive } from 'vue'

/**
 * Composable para gerenciar o estado global da sidebar e seus accordions.
 * Permite que o estado seja compartilhado entre componentes se necessário.
 */
const isCollapsed = ref(typeof window !== 'undefined' && window.innerWidth <= 768)
const openBase = ref(false)
const openCategories = reactive({})

export function useSidebar() {
  
  const toggleSidebar = () => {
    isCollapsed.value = !isCollapsed.value
    // Fecha todos os sub-menus ao colapsar a sidebar por UX
    if (isCollapsed.value) {
      openBase.value = false
      Object.keys(openCategories).forEach(key => {
        openCategories[key] = false
      })
    }
  }

  const toggleBase = () => {
    if (!isCollapsed.value) {
      openBase.value = !openBase.value
    }
  }

  const toggleCategory = (key) => {
    if (!isCollapsed.value) {
      // Se quiser política de apenas um accordion aberto por vez:
      // Object.keys(openCategories).forEach(k => { if(k !== key) openCategories[k] = false })
      openCategories[key] = !openCategories[key]
    }
  }

  return {
    isCollapsed,
    openBase,
    openCategories,
    toggleSidebar,
    toggleBase,
    toggleCategory,
  }
}
