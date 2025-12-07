import { createRouter, createWebHistory } from 'vue-router'

import UiShowdownView from '@/views/samples/UiShowdownView.vue'
import { AuthRoutes } from './auth.router.js'
import { Layout, MainLayout } from '@/layouts/index.js'
import { PageRoutes } from '@/router/pages.router.js'

const routes = [
  { path: '/ui', component: Layout, children: [{ path: '', component: UiShowdownView }] },
  { path: '/main', component: MainLayout, children: [{ path: '', component: UiShowdownView }] },
  AuthRoutes,
  PageRoutes,
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
export default router
