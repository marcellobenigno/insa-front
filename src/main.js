import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faLayerGroup, faSatellite } from '@fortawesome/free-solid-svg-icons'

import App from './App.vue'
import router from './router'

// Registra apenas os ícones que a aplicação usa (tree-shaking manual)
library.add(faLayerGroup, faSatellite)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.component('FontAwesomeIcon', FontAwesomeIcon)

app.mount('#app')
