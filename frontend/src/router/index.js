import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/access-logs',
    name: 'AccessLogs',
    component: () => import('../views/AccessLogs.vue')
  },
  {
    path: '/attack-logs',
    name: 'AttackLogs',
    component: () => import('../views/AttackLogs.vue')
  },
  {
    path: '/ipv6-stats',
    name: 'IPv6Stats',
    component: () => import('../views/IPv6Stats.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
