<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Usuarios</h1>
        <p class="page-sub">{{ total }} usuarios registrados en el sistema</p>
      </div>
      <button class="btn-primary" @click="abrirModal()">+ Nuevo Usuario</button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <input v-model="busqueda" class="input-search"
             placeholder="🔍 Buscar por nombre o correo..." @input="buscar" />
      <select v-model="filtroRol" class="select-filtro" @change="cargar">
        <option value="">Todos los roles</option>
        <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.nombre_rol }}</option>
      </select>
      <select v-model="filtroActivo" class="select-filtro" @change="cargar">
        <option value="">Todos</option>
        <option value="true">Activos</option>
        <option value="false">Inactivos</option>
      </select>
    </div>

    <!-- Tabla -->
    <div class="table-wrapper">
      <div v-if="cargando" class="estado-carga">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Usuario</th><th>Correo</th><th>Rol</th>
            <th>Estado</th><th>Fecha creación</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id">
            <td>
              <div class="usuario-cell">
                <span class="avatar-mini" :style="{ background: colorRol(u.rol_nombre) }">
                  {{ iniciales(u.nombre) }}
                </span>
                <strong>{{ u.nombre }}</strong>
              </div>
            </td>
            <td>{{ u.correo }}</td>
            <td><span :class="['badge', badgeRol(u.rol_nombre)]">{{ u.rol_nombre }}</span></td>
            <td>
              <span :class="['badge', u.activo ? 'badge-verde' : 'badge-gris']">
                {{ u.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>{{ formatFecha(u.fecha_creacion) }}</td>
            <td class="acciones">
              <button class="btn-icon" title="Editar"    @click="abrirModal(u)">✏️</button>
              <button class="btn-icon" title="Activar / Desactivar"
                      @click="toggleActivo(u)">{{ u.activo ? '🔒' : '🔓' }}</button>
              <button class="btn-icon" title="Eliminar"  @click="confirmarEliminar(u)">🗑️</button>
            </td>
          </tr>
          <tr v-if="!usuarios.length">
            <td colspan="6" class="sin-datos">No se encontraron usuarios.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear / Editar -->
    <div v-if="modalAbierto" class="overlay" @click.self="cerrarModal">
      <div class="modal">
        <h2 class="modal-titulo">{{ editando ? 'Editar Usuario' : 'Nuevo Usuario' }}</h2>
        <form @submit.prevent="guardar" class="form-grid">
          <div class="campo campo-full">
            <label>Nombre completo *</label>
            <input v-model="form.nombre" required placeholder="Ej. Javier Castillo" />
          </div>
          <div class="campo campo-full">
            <label>Correo electrónico *</label>
            <input v-model="form.correo" type="email" required
                   placeholder="usuario@premieroffshore.com" />
          </div>
          <div class="campo">
            <label>Rol *</label>
            <select v-model="form.id_rol" required>
              <option :value="null" disabled>Seleccionar...</option>
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.nombre_rol }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Estado</label>
            <select v-model="form.activo">
              <option :value="true">Activo</option>
              <option :value="false">Inactivo</option>
            </select>
          </div>

          <!-- Contraseña solo al crear o si se quiere cambiar -->
          <div class="campo campo-full" v-if="!editando">
            <label>Contraseña *</label>
            <input v-model="form.contrasena_hash" type="password"
                   :required="!editando" placeholder="Mínimo 8 caracteres" />
          </div>
          <div class="campo campo-full" v-else>
            <label>Nueva contraseña <span class="label-opcional">(dejar vacío para no cambiar)</span></label>
            <input v-model="form.contrasena_hash" type="password"
                   placeholder="••••••••" />
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="guardando">
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmar eliminar -->
    <div v-if="confirmandoEliminar" class="overlay" @click.self="confirmandoEliminar = false">
      <div class="modal modal-small">
        <h2 class="modal-titulo">¿Eliminar usuario?</h2>
        <p>¿Confirmas eliminar a <strong>{{ usuarioAEliminar?.nombre }}</strong>?
           Esta acción no se puede deshacer.</p>
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
import { usuariosAPI } from '../services/api.js'
import api from '../services/api.js'

const usuarios   = ref([])
const roles      = ref([])
const total      = ref(0)
const cargando   = ref(false)
const guardando  = ref(false)
const busqueda   = ref('')
const filtroRol  = ref('')
const filtroActivo = ref('')
const modalAbierto = ref(false)
const editando   = ref(false)
const form       = ref(formVacio())
const confirmandoEliminar = ref(false)
const usuarioAEliminar    = ref(null)

function formVacio() {
  return { nombre: '', correo: '', contrasena_hash: '', id_rol: null, activo: true }
}

function iniciales(nombre) {
  return nombre?.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase() || '??'
}

function formatFecha(f) {
  if (!f) return '—'
  return new Date(f).toLocaleDateString('es-DO', { dateStyle: 'medium' })
}

function colorRol(rol) {
  return { Administrador: '#1B6B3A', Supervisor: '#0a58ca', Agente: '#495057' }[rol] || '#999'
}

function badgeRol(rol) {
  return { Administrador: 'badge-verde', Supervisor: 'badge-azul', Agente: 'badge-gris' }[rol] || 'badge-gris'
}

let timer = null
function buscar() { clearTimeout(timer); timer = setTimeout(cargar, 400) }

async function cargar() {
  cargando.value = true
  try {
    const params = {}
    if (busqueda.value)    params.search = busqueda.value
    if (filtroRol.value)   params.rol    = filtroRol.value
    if (filtroActivo.value !== '') params.activo = filtroActivo.value
    const res = await usuariosAPI.listar(params)
    usuarios.value = res.data.results ?? res.data
    total.value    = res.data.count   ?? res.data.length
  } finally { cargando.value = false }
}

async function cargarRoles() {
  const res = await api.get('/roles/')
  roles.value = res.data.results ?? res.data
}

async function guardar() {
  guardando.value = true
  try {
    const payload = { ...form.value }
    // Si editando y no se ingresó contraseña, no la enviamos
    if (editando.value && !payload.contrasena_hash) {
      delete payload.contrasena_hash
    }
    if (editando.value) await usuariosAPI.editar(form.value.id, payload)
    else                await usuariosAPI.crear(payload)
    cerrarModal(); cargar()
  } finally { guardando.value = false }
}

async function toggleActivo(u) {
  await usuariosAPI.editar(u.id, { ...u, activo: !u.activo })
  cargar()
}

async function eliminar() {
  await usuariosAPI.eliminar(usuarioAEliminar.value.id)
  confirmandoEliminar.value = false
  cargar()
}

function abrirModal(u = null) {
  editando.value     = !!u
  form.value         = u ? { ...u, contrasena_hash: '' } : formVacio()
  modalAbierto.value = true
}
function cerrarModal() { modalAbierto.value = false; form.value = formVacio() }
function confirmarEliminar(u) { usuarioAEliminar.value = u; confirmandoEliminar.value = true }

onMounted(() => { cargar(); cargarRoles() })
</script>

<style scoped>
@import '../assets/crud.css';

.usuario-cell  { display: flex; align-items: center; gap: .6rem; }
.avatar-mini   {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: .72rem; font-weight: 700;
}
.label-opcional { font-weight: 400; color: #9ca3af; font-size: .78rem; }
</style>
