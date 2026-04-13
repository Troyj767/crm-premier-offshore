<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Log de Auditoría</h1>
        <p class="page-sub">Registro de todas las acciones críticas del sistema (RF-13)</p>
      </div>
      <button class="btn-secondary" @click="exportarCSV">⬇ Exportar CSV</button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <select v-model="filtroAccion" class="select-filtro" @change="cargar">
        <option value="">Todas las acciones</option>
        <option value="Creacion">Creación</option>
        <option value="Edicion">Edición</option>
        <option value="Eliminacion">Eliminación</option>
        <option value="Login">Login</option>
        <option value="Logout">Logout</option>
      </select>
      <select v-model="filtroTabla" class="select-filtro" @change="cargar">
        <option value="">Todas las tablas</option>
        <option value="Contactos">Contactos</option>
        <option value="Usuarios">Usuarios</option>
        <option value="Oportunidades">Oportunidades</option>
        <option value="Tareas">Tareas</option>
        <option value="Interacciones">Interacciones</option>
        <option value="Roles">Roles</option>
      </select>
      <select v-model="filtroUsuario" class="select-filtro" @change="cargar">
        <option value="">Todos los usuarios</option>
        <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.nombre }}</option>
      </select>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="stats-bar" v-if="!cargando">
      <div class="stat-item" v-for="s in estadisticas" :key="s.accion">
        <span :class="['stat-badge', colorAccion(s.accion)]">{{ s.accion }}</span>
        <span class="stat-num">{{ s.count }}</span>
      </div>
    </div>

    <!-- Tabla de logs -->
    <div class="table-wrapper">
      <div v-if="cargando" class="estado-carga">Cargando registros...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>#</th>
            <th>Fecha y Hora</th>
            <th>Usuario</th>
            <th>Acción</th>
            <th>Tabla</th>
            <th>ID Registro</th>
            <th>IP Origen</th>
            <th>Detalle</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="id-col">{{ log.id }}</td>
            <td class="fecha-col">{{ formatFecha(log.fecha_hora) }}</td>
            <td>
              <div class="usuario-cell">
                <span class="avatar-xs" :style="{ background: '#1B6B3A' }">
                  {{ iniciales(log.usuario_nombre) }}
                </span>
                {{ log.usuario_nombre }}
              </div>
            </td>
            <td>
              <span :class="['badge', colorAccion(log.accion)]">{{ log.accion }}</span>
            </td>
            <td><code class="tabla-nombre">{{ log.tabla_afectada }}</code></td>
            <td class="center-col">{{ log.id_registro ?? '—' }}</td>
            <td><code class="ip-text">{{ log.ip_origen ?? '—' }}</code></td>
            <td>
              <button v-if="log.valor_anterior || log.valor_nuevo"
                      class="btn-detalle" @click="verDetalle(log)">
                Ver cambio
              </button>
              <span v-else class="sin-cambio">—</span>
            </td>
          </tr>
          <tr v-if="!logs.length">
            <td colspan="8" class="sin-datos">No se encontraron registros de auditoría.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación simple -->
    <div class="paginacion" v-if="totalPaginas > 1">
      <button class="btn-secondary btn-sm" :disabled="paginaActual === 1"
              @click="cambiarPagina(paginaActual - 1)">‹ Anterior</button>
      <span class="pag-info">Página {{ paginaActual }} de {{ totalPaginas }}</span>
      <button class="btn-secondary btn-sm" :disabled="paginaActual === totalPaginas"
              @click="cambiarPagina(paginaActual + 1)">Siguiente ›</button>
    </div>

    <!-- Modal detalle de cambio -->
    <div v-if="detalleAbierto" class="overlay" @click.self="detalleAbierto = false">
      <div class="modal">
        <h2 class="modal-titulo">Detalle del Cambio</h2>
        <div class="detalle-cambio">
          <div class="cambio-col">
            <div class="cambio-header antes">Valor anterior</div>
            <pre class="cambio-pre">{{ formatJSON(logSeleccionado?.valor_anterior) }}</pre>
          </div>
          <div class="cambio-col">
            <div class="cambio-header despues">Valor nuevo</div>
            <pre class="cambio-pre">{{ formatJSON(logSeleccionado?.valor_nuevo) }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="detalleAbierto = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { auditoriaAPI, usuariosAPI } from '../services/api.js'

const logs          = ref([])
const usuarios      = ref([])
const total         = ref(0)
const cargando      = ref(false)
const filtroAccion  = ref('')
const filtroTabla   = ref('')
const filtroUsuario = ref('')
const paginaActual  = ref(1)
const porPagina     = 25

const detalleAbierto  = ref(false)
const logSeleccionado = ref(null)

const totalPaginas = computed(() => Math.ceil(total.value / porPagina))

// Conteo por acción para la barra de estadísticas
const estadisticas = computed(() => {
  const conteo = {}
  logs.value.forEach(l => { conteo[l.accion] = (conteo[l.accion] || 0) + 1 })
  return Object.entries(conteo).map(([accion, count]) => ({ accion, count }))
})

function iniciales(nombre) {
  return nombre?.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase() || '??'
}

function formatFecha(f) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-DO', { dateStyle: 'short', timeStyle: 'medium' })
}

function colorAccion(a) {
  return {
    Creacion:    'badge-verde',
    Edicion:     'badge-azul',
    Eliminacion: 'badge-rojo',
    Login:       'badge-gris',
    Logout:      'badge-gris',
  }[a] || 'badge-gris'
}

function formatJSON(val) {
  if (!val) return 'Sin datos'
  try { return JSON.stringify(JSON.parse(val), null, 2) }
  catch { return val }
}

async function cargar() {
  cargando.value = true
  try {
    const params = { ordering: '-fecha_hora', limit: porPagina, offset: (paginaActual.value - 1) * porPagina }
    if (filtroAccion.value)  params.accion  = filtroAccion.value
    if (filtroTabla.value)   params.tabla   = filtroTabla.value
    if (filtroUsuario.value) params.usuario = filtroUsuario.value
    const res = await auditoriaAPI.listar(params)
    logs.value  = res.data.results ?? res.data
    total.value = res.data.count   ?? res.data.length
  } finally { cargando.value = false }
}

function cambiarPagina(n) {
  paginaActual.value = n
  cargar()
}

function verDetalle(log) {
  logSeleccionado.value = log
  detalleAbierto.value  = true
}

function exportarCSV() {
  const encabezados = ['ID', 'Fecha', 'Usuario', 'Accion', 'Tabla', 'ID Registro', 'IP']
  const filas = logs.value.map(l => [
    l.id,
    formatFecha(l.fecha_hora),
    l.usuario_nombre,
    l.accion,
    l.tabla_afectada,
    l.id_registro ?? '',
    l.ip_origen ?? '',
  ])
  const csv = [encabezados, ...filas].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `auditoria_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  cargar()
  const res = await usuariosAPI.listar({})
  usuarios.value = res.data.results ?? res.data
})
</script>

<style scoped>
@import '../assets/crud.css';

/* Stats bar */
.stats-bar   { display: flex; gap: .6rem; flex-wrap: wrap; margin-bottom: 1rem; }
.stat-item   { display: flex; align-items: center; gap: .4rem;
               background: white; border-radius: 8px; padding: .4rem .8rem;
               box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.stat-num    { font-weight: 800; font-size: 1rem; color: #222; }

/* Tabla específica */
.id-col      { color: #aaa; font-size: .8rem; width: 40px; }
.fecha-col   { font-size: .8rem; white-space: nowrap; }
.center-col  { text-align: center; }
.tabla-nombre { background: #f3f4f6; padding: 2px 6px; border-radius: 4px;
                font-size: .78rem; color: #374151; }
.ip-text     { font-size: .78rem; color: #6c757d; }
.btn-detalle { background: none; border: 1px solid #d1d5db; border-radius: 6px;
               padding: 2px 10px; font-size: .78rem; cursor: pointer; color: #374151; }
.btn-detalle:hover { background: #f3f4f6; }
.sin-cambio  { color: #d1d5db; font-size: .8rem; }
.usuario-cell { display: flex; align-items: center; gap: .5rem; }
.avatar-xs   { width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0;
               display: flex; align-items: center; justify-content: center;
               color: white; font-size: .62rem; font-weight: 700; }

/* Paginación */
.paginacion  { display: flex; align-items: center; justify-content: center;
               gap: 1rem; margin-top: 1rem; }
.btn-sm      { padding: .35rem .9rem; font-size: .85rem; }
.pag-info    { font-size: .85rem; color: #6c757d; }

/* Modal detalle cambio */
.detalle-cambio { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.cambio-col     { display: flex; flex-direction: column; gap: .4rem; }
.cambio-header  { font-size: .75rem; font-weight: 700; text-transform: uppercase;
                  letter-spacing: .05em; padding: .3rem .6rem; border-radius: 4px; }
.antes          { background: #fee2e2; color: #991b1b; }
.despues        { background: #d1fae5; color: #065f46; }
.cambio-pre     { background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 6px;
                  padding: .75rem; font-size: .78rem; overflow-x: auto;
                  white-space: pre-wrap; word-break: break-word; min-height: 80px;
                  font-family: 'Courier New', monospace; color: #374151; }
</style>
