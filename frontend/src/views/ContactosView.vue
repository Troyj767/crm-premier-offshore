<template>
  <div class="page">
    <!-- Encabezado -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Contactos</h1>
        <p class="page-sub">{{ total }} contactos registrados</p>
      </div>
      <button class="btn-primary" @click="abrirModal()">+ Nuevo Contacto</button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <input v-model="busqueda" class="input-search" placeholder="🔍 Buscar por nombre, empresa..." @input="buscar" />
      <select v-model="filtroEstado" class="select-filtro" @change="cargar">
        <option value="">Todos los estados</option>
        <option value="Activo">Activo</option>
        <option value="Inactivo">Inactivo</option>
      </select>
      <select v-model="filtroAgente" class="select-filtro" @change="cargar">
        <option value="">Todos los agentes</option>
        <option v-for="u in agentes" :key="u.id" :value="u.id">{{ u.nombre }}</option>
      </select>
    </div>

    <!-- Tabla -->
    <div class="table-wrapper">
      <div v-if="cargando" class="estado-carga">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Nombre</th><th>Empresa</th><th>País</th>
            <th>Idioma</th><th>Agente</th><th>Estado</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in contactos" :key="c.id" @click="verDetalle(c)" class="fila-click">
            <td><strong>{{ c.nombre }}</strong></td>
            <td>{{ c.empresa || '—' }}</td>
            <td>{{ c.pais || '—' }}</td>
            <td>{{ c.idioma_preferido || '—' }}</td>
            <td>{{ c.agente_nombre || 'Sin asignar' }}</td>
            <td><span :class="['badge', c.estado === 'Activo' ? 'badge-verde' : 'badge-gris']">{{ c.estado }}</span></td>
            <td class="acciones" @click.stop>
              <button class="btn-icon" title="Editar"    @click="abrirModal(c)">✏️</button>
              <button class="btn-icon" title="Eliminar"  @click="confirmarEliminar(c)">🗑️</button>
            </td>
          </tr>
          <tr v-if="!contactos.length">
            <td colspan="7" class="sin-datos">No se encontraron contactos.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear / Editar -->
    <div v-if="modalAbierto" class="overlay" @click.self="cerrarModal">
      <div class="modal">
        <h2 class="modal-titulo">{{ editando ? 'Editar Contacto' : 'Nuevo Contacto' }}</h2>
        <form @submit.prevent="guardar" class="form-grid">
          <div class="campo">
            <label>Nombre *</label>
            <input v-model="form.nombre" required />
          </div>
          <div class="campo">
            <label>Empresa</label>
            <input v-model="form.empresa" />
          </div>
          <div class="campo">
            <label>Teléfono</label>
            <input v-model="form.telefono" />
          </div>
          <div class="campo">
            <label>Correo</label>
            <input v-model="form.correo" type="email" />
          </div>
          <div class="campo">
            <label>País</label>
            <input v-model="form.pais" />
          </div>
          <div class="campo">
            <label>Idioma preferido</label>
            <select v-model="form.idioma_preferido">
              <option value="Español">Español</option>
              <option value="Inglés">Inglés</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div class="campo">
            <label>Estado</label>
            <select v-model="form.estado">
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
            </select>
          </div>
          <div class="campo">
            <label>Agente asignado</label>
            <select v-model="form.id_agente_asignado">
              <option :value="null">Sin asignar</option>
              <option v-for="u in agentes" :key="u.id" :value="u.id">{{ u.nombre }}</option>
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

    <!-- Modal Detalle -->
    <div v-if="detalleAbierto" class="overlay" @click.self="detalleAbierto = false">
      <div class="modal modal-wide">
        <h2 class="modal-titulo">{{ contactoSeleccionado?.nombre }}</h2>
        <p class="detalle-sub">{{ contactoSeleccionado?.empresa }} — {{ contactoSeleccionado?.pais }}</p>

        <div class="tabs">
          <button :class="['tab', tabActiva === 'info'     && 'tab-activa']" @click="tabActiva = 'info'">Info</button>
          <button :class="['tab', tabActiva === 'historial' && 'tab-activa']" @click="cargarHistorial">Historial</button>
          <button :class="['tab', tabActiva === 'pipeline'  && 'tab-activa']" @click="cargarPipeline">Pipeline</button>
        </div>

        <!-- Tab: Info -->
        <div v-if="tabActiva === 'info'" class="detalle-grid">
          <div><span class="label">Teléfono</span><span>{{ contactoSeleccionado?.telefono || '—' }}</span></div>
          <div><span class="label">Correo</span><span>{{ contactoSeleccionado?.correo || '—' }}</span></div>
          <div><span class="label">Idioma</span><span>{{ contactoSeleccionado?.idioma_preferido || '—' }}</span></div>
          <div><span class="label">Estado</span><span>{{ contactoSeleccionado?.estado }}</span></div>
          <div><span class="label">Agente</span><span>{{ contactoSeleccionado?.agente_nombre || 'Sin asignar' }}</span></div>
          <div><span class="label">Creado</span><span>{{ formatFecha(contactoSeleccionado?.fecha_creacion) }}</span></div>
        </div>

        <!-- Tab: Historial de interacciones -->
        <div v-if="tabActiva === 'historial'" class="lista-items">
          <div v-for="i in historial" :key="i.id" class="item-card">
            <div class="item-header">
              <span class="badge badge-azul">{{ i.tipo_interaccion }}</span>
              <span class="fecha-small">{{ formatFecha(i.fecha_hora) }}</span>
            </div>
            <p>{{ i.resultado }}</p>
            <small v-if="i.notas_internas" class="notas">📝 {{ i.notas_internas }}</small>
          </div>
          <p v-if="!historial.length" class="sin-datos">Sin interacciones registradas.</p>
        </div>

        <!-- Tab: Pipeline -->
        <div v-if="tabActiva === 'pipeline'" class="lista-items">
          <div v-for="o in pipelineContacto" :key="o.id" class="item-card">
            <div class="item-header">
              <strong>{{ o.titulo }}</strong>
              <span :class="['badge', badgeEtapa(o.etapa)]">{{ o.etapa }}</span>
            </div>
            <p>Monto: <strong>${{ o.monto_estimado }}</strong> | Probabilidad: <strong>{{ o.probabilidad_pct }}%</strong></p>
          </div>
          <p v-if="!pipelineContacto.length" class="sin-datos">Sin oportunidades registradas.</p>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="detalleAbierto = false">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- Confirmar eliminar -->
    <div v-if="confirmandoEliminar" class="overlay" @click.self="confirmandoEliminar = false">
      <div class="modal modal-small">
        <h2 class="modal-titulo">¿Eliminar contacto?</h2>
        <p>Esta acción eliminará también todas las interacciones y tareas asociadas a <strong>{{ contactoAEliminar?.nombre }}</strong>.</p>
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
import { contactosAPI, usuariosAPI } from '../services/api.js'

// ─── Estado ──────────────────────────────────────────────────────────────────
const contactos   = ref([])
const agentes     = ref([])
const total       = ref(0)
const cargando    = ref(false)
const guardando   = ref(false)
const busqueda    = ref('')
const filtroEstado = ref('')
const filtroAgente = ref('')

const modalAbierto = ref(false)
const editando     = ref(false)
const form         = ref(formVacio())

const detalleAbierto       = ref(false)
const contactoSeleccionado = ref(null)
const tabActiva            = ref('info')
const historial            = ref([])
const pipelineContacto     = ref([])

const confirmandoEliminar = ref(false)
const contactoAEliminar   = ref(null)

// ─── Helpers ─────────────────────────────────────────────────────────────────
function formVacio() {
  return { nombre: '', empresa: '', telefono: '', correo: '',
           pais: '', idioma_preferido: 'Español', estado: 'Activo', id_agente_asignado: null }
}

function formatFecha(f) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-DO', { dateStyle: 'medium', timeStyle: 'short' })
}

function badgeEtapa(e) {
  const mapa = { 'Propuesta': 'badge-azul', 'Negociacion': 'badge-naranja',
                 'Cerrado Ganado': 'badge-verde', 'Cerrado Perdido': 'badge-gris' }
  return mapa[e] || 'badge-gris'
}

let timer = null
function buscar() {
  clearTimeout(timer)
  timer = setTimeout(cargar, 400)
}

// ─── API Calls ───────────────────────────────────────────────────────────────
async function cargar() {
  cargando.value = true
  try {
    const params = {}
    if (busqueda.value)    params.search = busqueda.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    if (filtroAgente.value) params.agente = filtroAgente.value
    const res = await contactosAPI.listar(params)
    contactos.value = res.data.results ?? res.data
    total.value     = res.data.count   ?? res.data.length
  } finally {
    cargando.value = false
  }
}

async function cargarAgentes() {
  const res = await usuariosAPI.listar({ search: '' })
  agentes.value = (res.data.results ?? res.data).filter(u => u.activo)
}

async function guardar() {
  guardando.value = true
  try {
    if (editando.value) {
      await contactosAPI.editar(form.value.id, form.value)
    } else {
      await contactosAPI.crear(form.value)
    }
    cerrarModal()
    cargar()
  } finally {
    guardando.value = false
  }
}

async function eliminar() {
  await contactosAPI.eliminar(contactoAEliminar.value.id)
  confirmandoEliminar.value = false
  cargar()
}

async function cargarHistorial() {
  tabActiva.value = 'historial'
  const res = await contactosAPI.historial(contactoSeleccionado.value.id)
  historial.value = res.data
}

async function cargarPipeline() {
  tabActiva.value = 'pipeline'
  const res = await contactosAPI.pipeline(contactoSeleccionado.value.id)
  pipelineContacto.value = res.data
}

// ─── Modal ───────────────────────────────────────────────────────────────────
function abrirModal(contacto = null) {
  editando.value     = !!contacto
  form.value         = contacto ? { ...contacto } : formVacio()
  modalAbierto.value = true
}

function cerrarModal() {
  modalAbierto.value = false
  form.value = formVacio()
}

function verDetalle(c) {
  contactoSeleccionado.value = c
  tabActiva.value            = 'info'
  historial.value            = []
  pipelineContacto.value     = []
  detalleAbierto.value       = true
}

function confirmarEliminar(c) {
  contactoAEliminar.value   = c
  confirmandoEliminar.value = true
}

onMounted(() => { cargar(); cargarAgentes() })
</script>

<style scoped>
@import '../assets/crud.css';
</style>
