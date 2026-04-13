<template>
  <div id="app">
    <template v-if="!autenticado">
      <router-view />
    </template>

    <template v-else>
      <div class="layout">

        <aside :class="['sidebar', sidebarColapsado && 'sidebar--mini']">
          <div class="sidebar__logo">
            <span class="logo-icono">🏢</span>
            <span class="logo-texto" v-if="!sidebarColapsado">Premier<br><strong>CRM</strong></span>
          </div>

          <nav class="sidebar__nav">
            <router-link to="/dashboard" class="nav-item" title="Dashboard">
              <span class="nav-icono">📊</span>
              <span class="nav-label" v-if="!sidebarColapsado">Dashboard</span>
            </router-link>
            <router-link to="/contactos" class="nav-item" title="Contactos">
              <span class="nav-icono">👥</span>
              <span class="nav-label" v-if="!sidebarColapsado">Contactos</span>
            </router-link>
            <router-link to="/pipeline" class="nav-item" title="Pipeline">
              <span class="nav-icono">📈</span>
              <span class="nav-label" v-if="!sidebarColapsado">Pipeline</span>
            </router-link>
            <router-link to="/tareas" class="nav-item" title="Tareas">
              <span class="nav-icono">✅</span>
              <span class="nav-label" v-if="!sidebarColapsado">Tareas</span>
              <span class="nav-badge" v-if="tareasUrgentes > 0 && !sidebarColapsado">{{ tareasUrgentes }}</span>
            </router-link>

            <template v-if="esAdmin">
              <div class="nav-separator" v-if="!sidebarColapsado">
                <span>Administración</span>
              </div>
              <router-link to="/usuarios" class="nav-item" title="Usuarios">
                <span class="nav-icono">👤</span>
                <span class="nav-label" v-if="!sidebarColapsado">Usuarios</span>
              </router-link>
              <router-link to="/auditoria" class="nav-item" title="Auditoría">
                <span class="nav-icono">🔍</span>
                <span class="nav-label" v-if="!sidebarColapsado">Auditoría</span>
              </router-link>
            </template>
          </nav>

          <button class="sidebar__toggle" @click="sidebarColapsado = !sidebarColapsado"
                  :title="sidebarColapsado ? 'Expandir' : 'Colapsar'">
            {{ sidebarColapsado ? '›' : '‹' }}
          </button>
        </aside>

        <div class="main">
          <header class="topbar">
            <div class="topbar__titulo">{{ tituloActual }}</div>
            <div class="topbar__right">
              <div class="topbar__usuario">
                <span class="usuario-avatar">{{ iniciales }}</span>
                <div class="usuario-info" v-if="usuarioActual">
                  <span class="usuario-nombre">{{ usuarioActual.nombre }}</span>
                  <span class="usuario-rol">{{ usuarioActual.rol }}</span>
                </div>
              </div>
              <button class="btn-logout" @click="cerrarSesion" title="Cerrar sesión">⏏</button>
            </div>
          </header>

          <main class="contenido">
            <router-view />
          </main>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { tareasAPI } from './services/api.js'

const router = useRouter()
const route  = useRoute()

const sidebarColapsado = ref(false)
const tareasUrgentes   = ref(0)
const usuarioActual    = ref(null)

// CAMBIO CLAVE: ref en vez de computed para que sea reactivo tras window.location
const autenticado = ref(!!localStorage.getItem('access_token'))

window.addEventListener('storage-updated', () => {
  autenticado.value = !!localStorage.getItem('access_token')
  const d = localStorage.getItem('usuario')
  if (d) usuarioActual.value = JSON.parse(d)
})

const esAdmin = computed(() => {
  const rol = usuarioActual.value?.rol
  return rol === 'Administrador' || rol === 'Supervisor'
})

const iniciales = computed(() => {
  const n = usuarioActual.value?.nombre || ''
  return n.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase()
})

const titulos = {
  '/dashboard': 'Dashboard',
  '/contactos': 'Contactos',
  '/pipeline':  'Pipeline de Ventas',
  '/tareas':    'Tareas',
  '/usuarios':  'Gestión de Usuarios',
  '/auditoria': 'Log de Auditoría',
}
const tituloActual = computed(() => titulos[route.path] || 'CRM')

function cerrarSesion() {
  localStorage.clear()
  autenticado.value = false
  usuarioActual.value = null
  router.push('/login')
}

async function cargarUrgentes() {
  try {
    const res = await tareasAPI.urgentes()
    tareasUrgentes.value = res.data.length
  } catch {}
}

onMounted(() => {
  const datos = localStorage.getItem('usuario')
  if (datos) usuarioActual.value = JSON.parse(datos)
  if (autenticado.value) cargarUrgentes()
})

watch(() => route.path, () => {
  if (autenticado.value) cargarUrgentes()
})
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Arial', sans-serif; background: #f0f2f5; color: #222; }
a    { text-decoration: none; color: inherit; }
#app { height: 100vh; }

.layout  { display: flex; height: 100vh; overflow: hidden; }
.main    { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.contenido { flex: 1; overflow-y: auto; }

.sidebar {
  width: 220px;
  background: #1B6B3A;
  display: flex;
  flex-direction: column;
  transition: width .25s ease;
  flex-shrink: 0;
  position: relative;
}
.sidebar--mini { width: 64px; }

.sidebar__logo {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,.12);
  min-height: 68px;
}
.logo-icono { font-size: 1.6rem; flex-shrink: 0; }
.logo-texto { color: white; font-size: .88rem; line-height: 1.3; }
.logo-texto strong { font-size: 1.05rem; }

.sidebar__nav { flex: 1; padding: .75rem 0; display: flex; flex-direction: column; gap: 2px; }

.nav-item {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .6rem 1rem;
  color: rgba(255,255,255,.75);
  font-size: .88rem;
  font-weight: 500;
  border-radius: 0;
  transition: background .15s, color .15s;
  position: relative;
  white-space: nowrap;
  overflow: hidden;
}
.nav-item:hover { background: rgba(255,255,255,.1); color: white; }
.nav-item.router-link-active { background: rgba(255,255,255,.18); color: white; border-left: 3px solid white; }
.nav-icono { font-size: 1.1rem; flex-shrink: 0; width: 24px; text-align: center; }
.nav-label { flex: 1; }
.nav-badge {
  background: #ff4444; color: white; border-radius: 99px;
  font-size: .7rem; font-weight: 700; padding: 1px 6px; min-width: 18px; text-align: center;
}
.nav-separator {
  padding: .75rem 1rem .25rem;
  font-size: .7rem;
  font-weight: 700;
  color: rgba(255,255,255,.4);
  text-transform: uppercase;
  letter-spacing: .08em;
}

.sidebar__toggle {
  background: rgba(255,255,255,.1);
  border: none;
  color: white;
  font-size: 1.1rem;
  padding: .5rem;
  cursor: pointer;
  text-align: center;
  transition: background .15s;
}
.sidebar__toggle:hover { background: rgba(255,255,255,.2); }

.topbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.topbar__titulo { font-size: 1.1rem; font-weight: 700; color: #1B6B3A; }
.topbar__right  { display: flex; align-items: center; gap: 1rem; }

.topbar__usuario { display: flex; align-items: center; gap: .6rem; }
.usuario-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: #1B6B3A; color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 700;
}
.usuario-info   { display: flex; flex-direction: column; }
.usuario-nombre { font-size: .82rem; font-weight: 600; color: #222; }
.usuario-rol    { font-size: .72rem; color: #888; }

.btn-logout {
  background: none; border: 1px solid #e5e7eb; border-radius: 8px;
  padding: .35rem .6rem; cursor: pointer; font-size: 1rem;
  color: #666; transition: all .15s;
}
.btn-logout:hover { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }
</style>