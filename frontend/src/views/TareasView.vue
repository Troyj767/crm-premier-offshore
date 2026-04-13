<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Tareas</h1>
        <p class="page-sub">{{ total }} tareas registradas</p>
      </div>
      <button class="btn-primary" @click="abrirModal()">+ Nueva Tarea</button>
    </div>

    <!-- Alertas de tareas urgentes -->
    <div v-if="urgentes.length" class="alerta-urgente">
      ⚠️ <strong>{{ urgentes.length }} tarea(s)</strong> vencidas o por vencer en las próximas 48 horas.
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <input v-model="busqueda" class="input-search" placeholder="🔍 Buscar tareas..." @input="buscar" />
      <select v-model="filtroEstado" class="select-filtro" @change="cargar">
        <option value="">Todos los estados</option>
        <option v-for="e in estados" :key="e" :value="e">{{ e }}</option>
      </select>
      <select v-model="filtroPrioridad" class="select-filtro" @change="cargar">
        <option value="">Todas las prioridades</option>
        <option v-for="p in prioridades" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <!-- Tabla -->
    <div class="table-wrapper">
      <div v-if="cargando" class="estado-carga">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Título</th><th>Contacto</th><th>Agente</th>
            <th>Fecha límite</th><th>Prioridad</th><th>Estado</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tareas" :key="t.id" :class="t.vencida ? 'fila-vencida' : ''">
            <td>
              <strong>{{ t.titulo }}</strong>
              <div class="sub-texto">{{ t.descripcion.slice(0, 60) }}{{ t.descripcion.length > 60 ? '…' : '' }}</div>
            </td>
            <td>{{ t.contacto_nombre || '—' }}</td>
            <td>{{ t.agente_nombre }}</td>
            <td>
              <span :class="t.vencida ? 'text-rojo' : ''">{{ formatFecha(t.fecha_limite) }}</span>
              <span v-if="t.vencida" class="badge badge-rojo ml-1">Vencida</span>
            </td>
            <td><span :class="['badge', badgePrioridad(t.prioridad)]">{{ t.prioridad }}</span></td>
            <td><span :class="['badge', badgeEstado(t.estado)]">{{ t.estado }}</span></td>
            <td class="acciones">
              <button class="btn-icon" @click="abrirModal(t)"     title="Editar">✏️</button>
              <button class="btn-icon" @click="confirmarEliminar(t)" title="Eliminar">🗑️</button>
            </td>
          </tr>
          <tr v-if="!tareas.length">
            <td colspan="7" class="sin-datos">No se encontraron tareas.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear / Editar -->
    <div v-if="modalAbierto" class="overlay" @click.self="cerrarModal">
      <div class="modal">
        <h2 class="modal-titulo">{{ editando ? 'Editar Tarea' : 'Nueva Tarea' }}</h2>
        <form @submit.prevent="guardar" class="form-grid">
          <div class="campo campo-full">
            <label>Título *</label>
            <input v-model="form.titulo" required />
          </div>
          <div class="campo campo-full">
            <label>Descripción *</label>
            <textarea v-model="form.descripcion" rows="3" required></textarea>
          </div>
          <div class="campo">
            <label>Fecha límite *</label>
            <input v-model="form.fecha_limite" type="datetime-local" required />
          </div>
          <div class="campo">
            <label>Prioridad</label>
            <select v-model="form.prioridad">
              <option v-for="p in prioridades" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Estado</label>
            <select v-model="form.estado">
              <option v-for="e in estados" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Agente asignado *</label>
            <select v-model="form.id_usuario_asignado" required>
              <option :value="null" disabled>Seleccionar...</option>
              <option v-for="u in agentes" :key="u.id" :value="u.id">{{ u.nombre }}</option>
            </select>
          </div>
          <div class="campo campo-full">
            <label>Contacto relacionado</label>
            <select v-model="form.id_contacto">
              <option :value="null">Sin contacto</option>
              <option v-for="c in contactos" :key="c.id" :value="c.id">{{ c.nombre }} — {{ c.empresa }}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button type="submit"  class="btn-primary"   :disabled="guardando">
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmar eliminar -->
    <div v-if="confirmandoEliminar" class="overlay" @click.self="confirmandoEliminar = false">
      <div class="modal modal-small">
        <h2 class="modal-titulo">¿Eliminar tarea?</h2>
        <p>¿Confirmas eliminar la tarea <strong>{{ tareaAEliminar?.titulo }}</strong>?</p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="confirmandoEliminar = false">Cancelar</button>
          <button class="btn-danger"    @click="eliminar">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { tareasAPI, usuariosAPI, contactosAPI } from '../services/api.js'

const tareas         = ref([])
const urgentes       = ref([])
const agentes        = ref([])
const contactos      = ref([])
const total          = ref(0)
const cargando       = ref(false)
const guardando      = ref(false)
const busqueda       = ref('')
const filtroEstado   = ref('')
const filtroPrioridad = ref('')
const modalAbierto   = ref(false)
const editando       = ref(false)
const form           = ref(formVacio())
const confirmandoEliminar = ref(false)
const tareaAEliminar = ref(null)

const estados    = ['Pendiente', 'En Progreso', 'Completada', 'Vencida']
const prioridades = ['Baja', 'Normal', 'Alta', 'Urgente']

function formVacio() {
  return { titulo: '', descripcion: '', fecha_limite: '', estado: 'Pendiente',
           prioridad: 'Normal', id_usuario_asignado: null, id_contacto: null }
}

function formatFecha(f) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-DO', { dateStyle: 'short', timeStyle: 'short' })
}

function badgePrioridad(p) {
  return { Urgente: 'badge-rojo', Alta: 'badge-naranja', Normal: 'badge-azul', Baja: 'badge-gris' }[p] || 'badge-gris'
}

function badgeEstado(e) {
  return { Completada: 'badge-verde', 'En Progreso': 'badge-azul', Vencida: 'badge-rojo', Pendiente: 'badge-gris' }[e] || 'badge-gris'
}

let timer = null
function buscar() { clearTimeout(timer); timer = setTimeout(cargar, 400) }

async function cargar() {
  cargando.value = true
  try {
    const params = {}
    if (busqueda.value)      params.search    = busqueda.value
    if (filtroEstado.value)  params.estado    = filtroEstado.value
    if (filtroPrioridad.value) params.prioridad = filtroPrioridad.value
    const res = await tareasAPI.listar(params)
    tareas.value = res.data.results ?? res.data
    total.value  = res.data.count   ?? res.data.length
    // Cargar urgentes
    const urg = await tareasAPI.urgentes()
    urgentes.value = urg.data
  } finally { cargando.value = false }
}

async function guardar() {
  guardando.value = true
  try {
    if (editando.value) await tareasAPI.editar(form.value.id, form.value)
    else                await tareasAPI.crear(form.value)
    cerrarModal(); cargar()
  } finally { guardando.value = false }
}

async function eliminar() {
  await tareasAPI.eliminar(tareaAEliminar.value.id)
  confirmandoEliminar.value = false
  cargar()
}

function abrirModal(t = null) {
  editando.value     = !!t
  form.value         = t ? { ...t } : formVacio()
  modalAbierto.value = true
}
function cerrarModal() { modalAbierto.value = false; form.value = formVacio() }
function confirmarEliminar(t) { tareaAEliminar.value = t; confirmandoEliminar.value = true }

onMounted(async () => {
  cargar()
  const [ua, ca] = await Promise.all([usuariosAPI.listar({}), contactosAPI.listar({})])
  agentes.value  = ua.data.results ?? ua.data
  contactos.value = ca.data.results ?? ca.data
})
</script>

<style scoped>
@import '../assets/crud.css';
</style>
