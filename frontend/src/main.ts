import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import Catalog from './pages/Catalog.vue'
import './style.css'
import './complexity.css'

const router = createRouter({history: createWebHistory(), routes: [
  {path: '/', component: Home},
  {path: '/problems', component: Catalog},
  {path: '/problems/:id', component: () => import('./pages/Workspace.vue')},
  {path: '/:pathMatch(.*)*', redirect: '/'},
]})
createApp(App).use(router).mount('#app')
