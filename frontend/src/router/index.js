import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import { isLoggedIn } from '../services/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/access-logs',
    name: 'AccessLogs',
    component: () => import('../views/AccessLogs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/attack-logs',
    name: 'AttackLogs',
    component: () => import('../views/AttackLogs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/firewall-config',
    name: 'FirewallConfig',
    component: () => import('../views/FirewallConfig.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/protected-apps',
    name: 'ProtectedApps',
    component: () => import('../views/ProtectedApps.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/protected-apps/add',
    name: 'AddProtectedApp',
    component: () => import('../views/AddProtectedApp.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/protected-apps/:id',
    name: 'EditProtectedApp',
    component: () => import('../views/EditProtectedApp.vue'),
    meta: { requiresAuth: true }
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 调试信息
  console.log('Navigation guard triggered:', {
    to: to.path,
    from: from.path,
    isLoggedIn: isLoggedIn(),
    token: localStorage.getItem('token')
  })
  
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth && !isLoggedIn()) {
    // 需要认证但未登录，重定向到登录页
    console.log('Requires auth but not logged in, redirecting to login')
    next('/login')
  } else if (to.path === '/login' && isLoggedIn()) {
    // 已登录但访问登录页，重定向到首页
    console.log('Already logged in, redirecting to home')
    next('/')
  } else {
    // 其他情况，正常导航
    console.log('Normal navigation')
    next()
  }
})

export default router
