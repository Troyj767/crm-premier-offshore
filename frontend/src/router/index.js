import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/',             redirect: '/dashboard' },
  { path: '/login',        component: () => import('../views/LoginView.vue'),        meta: { public: true } },
  { path: '/dashboard',    component: () => import('../views/DashboardView.vue'),    meta: { title: 'Dashboard' } },
  { path: '/contactos',    component: () => import('../views/ContactosView.vue'),    meta: { title: 'Contactos' } },
  { path: '/pipeline',     component: () => import('../views/PipelineView.vue'),     meta: { title: 'Pipeline' } },
  { path: '/tareas',       component: () => import('../views/TareasView.vue'),       meta: { title: 'Tareas' } },
  { path: '/usuarios',     component: () => import('../views/UsuariosView.vue'),     meta: { title: 'Usuarios' } },
  { path: '/auditoria',    component: () => import('../views/AuditoriaView.vue'),    meta: { title: 'Auditoria' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router