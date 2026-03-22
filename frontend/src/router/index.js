import { createRouter, createWebHistory } from 'vue-router'
import GraphExplorer from '../views/GraphExplorer.vue'

const routes = [
  { path: '/', name: 'graph', component: GraphExplorer },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/disease/:efoId', name: 'disease', component: () => import('../views/DiseaseReport.vue'), props: true },
  { path: '/compare', name: 'compare', component: () => import('../views/Compare.vue') },
  { path: '/target/:symbol', name: 'target', component: () => import('../views/TargetDetail.vue'), props: true },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
