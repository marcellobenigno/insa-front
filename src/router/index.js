import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'inicio', component: () => import('@/views/InicioView.vue') },
  { path: '/mapa', name: 'map', component: () => import('@/views/HomeView.vue') },
  { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
]

// Hash history: o build é publicado no GitHub Pages sem rewrite de servidor
// para SPA — history mode causaria 404 num refresh direto em /dashboard.
export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
})
