import { ref, watch } from 'vue'

const isDark = ref(localStorage.getItem('insa-theme') !== 'light')

function applyTheme(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

applyTheme(isDark.value)

watch(isDark, (val) => {
  applyTheme(val)
  localStorage.setItem('insa-theme', val ? 'dark' : 'light')
})

export function useTheme() {
  return {
    isDark,
    toggleTheme: () => { isDark.value = !isDark.value },
  }
}
