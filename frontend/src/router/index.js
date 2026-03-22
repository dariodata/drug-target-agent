import { createRouter, createWebHistory } from 'vue-router'
import GraphExplorer from '../views/GraphExplorer.vue'

const routes = [
  { path: '/', name: 'graph', component: GraphExplorer },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/compare', name: 'compare', component: () => import('../views/Compare.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
