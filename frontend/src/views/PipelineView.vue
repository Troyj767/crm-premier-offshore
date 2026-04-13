<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Pipeline de Ventas</h1>
        <p class="page-sub">Valor total: <strong>${{ valorTotal.toLocaleString('es-DO') }}</strong></p>
      </div>
      <button class="btn-primary" @click="abrirModal()">+ Nueva Oportunidad</button>
    </div>

    <!-- Tablero Kanban -->
    <div class="kanban-board" v-if="!cargando">
      <div v-for="etapa in etapas" :key="etapa.key" class="kanban-col">
        <div class="kanban-col-header" :style="{ borderTopColor: etapa.color }">
          <span class="kanban-col-titulo">{{ etapa.label }}</span>
          <span class="kanban-badge">{{ oportunidadesPorEtapa(etapa.key).length }}</span>
        </div>

        <div class="kanban-cards">
          <div
            v-for="op in oportunidadesPorEtapa(etapa.key)"
            :key="op.id"
            class="kanban-card"
          >
            <div class="kcard-titulo">{{ op.titulo }}</div>
            <div class="kcard-contacto">👤 {{ op.contacto_nombre }}</div>
            <div class="kcard-monto">${{ Number(op.monto_estimado).toLocaleString('es-DO') }}</div>
            <div class="kcard-prob">
              <div class="prob-bar">
                <div class="prob-fill" :style="{ width: op.probabilidad_pct + '%', background: etapa.color }"></div>
              </div>
              <span>{{ op.probabilidad_pct }}%</span>
            </div>
            <div class="kcard-acciones">
              <button class="btn-icon-sm" @click="abrirModal(op)" title="Editar">✏️</button>
              <button class="btn-icon-sm" @click="moverEtapa(op, 'anterior')" title="Retroceder" :disabled="etapa.key === etapas[0].key">◀</button>
              <button class="btn-icon-sm" @click="moverEtapa(op, 'siguiente')" title="Avanzar"   :disabled="etapa.key === etapas[etapas.length-1].key">▶</button>
              <button class="btn-icon-sm" @click="confirmarEliminar(op)" title="Eliminar">🗑️</button>
            </div>
          </div>
          <div v-if="!oportunidadesPorEtapa(etapa.key).length" class="kanban-vacio">Sin oportunidades</div>
        </div>
      </div>
    </div>
    <div v-else class="estado-carga">Cargando pipeline...</div>

    <!-- Modal Crear / Editar -->
    <div v-if="modalAbierto" class="overlay" @click.self="cerrarModal">
      <div class="modal">
        <h2 class="modal-titulo">{{ editando ? 'Editar Oportunidad' : 'Nueva Oportunidad' }}</h2>
        <form @submit.prevent="guardar" class="form-grid">
          <div class="campo campo-full">
            <label>Título *</label>
            <input v-model="form.titulo" required />
          </div>
          <div class="campo">
            <label>Contacto *</label>
            <select v-model="form.id_contacto" required>
              <option :value="null" disabled>Seleccionar...</option>
              <option v-for="c in contactos" :key="c.id" :value="c.id">{{ c.nombre }} — {{ c.empresa }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Agente responsable *</label>
            <select v-model="form.id_usuario" required>
              <option :value="null" disabled>Seleccionar...</option>
              <option v-for="u in agentes" :key="u.id" :value="u.id">{{ u.nombre }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Etapa</label>
            <select v-model="form.etapa">
              <option v-for="e in etapas" :key="e.key" :value="e.key">{{ e.label }}</option>
            </select>
          </div>
          <div class="campo">
            <label>Monto estimado ($)</label>
            <input v-model="form.monto_estimado" type="number" min="0" step="0.01" />
          </div>
          <div class="campo">
            <label>Probabilidad (%) {{ form.probabilidad_pct }}%</label>
            <input v-model="form.probabilidad_pct" type="range" min="0" max="100" />
          </div>
          <div class="campo">
            <label>Fecha cierre estimada</label>
            <input v-model="form.fecha_cierre_est" type="date" />
          </div>
          <div class="campo campo-full">
            <label>Descripción</label>
            <textarea v-model="form.descripcion" rows="3"></textarea>
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
        <h2 class="modal-titulo">¿Eliminar oportunidad?</h2>
        <p>¿Eliminar <strong>{{ opAEliminar?.titulo }}</strong>?</p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="confirmandoEliminar = false">Cancelar</button>
          <button class="btn-danger"    @click="eliminar">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { oportunidadesAPI, contactosAPI, usuariosAPI } from '../services/api.js'

const oportunidades = ref([])
const contactos     = ref([])
const agentes       = ref([])
const cargando      = ref(false)
const guardando     = ref(false)
const modalAbierto  = ref(false)
const editando      = ref(false)
const form          = ref(formVacio())
const confirmandoEliminar = ref(false)
const opAEliminar   = ref(null)

const etapas = [
  { key: 'Prospecto',       label: 'Prospecto',        color: '#6c757d' },
  { key: 'Contactado',      label: 'Contactado',        color: '#0d6efd' },
  { key: 'Propuesta',       label: 'Propuesta',         color: '#fd7e14' },
  { key: 'Negociacion',     label: 'Negociación',       color: '#ffc107' },
  { key: 'Cerrado Ganado',  label: 'Cerrado ✅',        color: '#1B6B3A' },
  { key: 'Cerrado Perdido', label: 'Perdido ❌',        color: '#dc3545' },
]

function formVacio() {
  return { titulo: '', id_contacto: null, id_usuario: null, etapa: 'Prospecto',
           monto_estimado: 0, probabilidad_pct: 0, fecha_cierre_est: '', descripcion: '' }
}

const valorTotal = computed(() =>
  oportunidades.value
    .filter(o => !['Cerrado Perdido'].includes(o.etapa))
    .reduce((s, o) => s + parseFloat(o.monto_estimado || 0), 0)
)

function oportunidadesPorEtapa(etapa) {
  return oportunidades.value.filter(o => o.etapa === etapa)
}

async function cargar() {
  cargando.value = true
  try {
    const res = await oportunidadesAPI.listar({})
    oportunidades.value = res.data.results ?? res.data
  } finally { cargando.value = false }
}

async function guardar() {
  guardando.value = true
  try {
    if (editando.value) await oportunidadesAPI.editar(form.value.id, form.value)
    else                await oportunidadesAPI.crear(form.value)
    cerrarModal(); cargar()
  } finally { guardando.value = false }
}

async function moverEtapa(op, direccion) {
  const idx = etapas.findIndex(e => e.key === op.etapa)
  const nuevo = direccion === 'siguiente' ? etapas[idx + 1]?.key : etapas[idx - 1]?.key
  if (!nuevo) return
  await oportunidadesAPI.editar(op.id, { ...op, etapa: nuevo })
  cargar()
}

async function eliminar() {
  await oportunidadesAPI.eliminar(opAEliminar.value.id)
  confirmandoEliminar.value = false
  cargar()
}

function abrirModal(op = null) {
  editando.value     = !!op
  form.value         = op ? { ...op } : formVacio()
  modalAbierto.value = true
}
function cerrarModal() { modalAbierto.value = false; form.value = formVacio() }
function confirmarEliminar(op) { opAEliminar.value = op; confirmandoEliminar.value = true }

onMounted(async () => {
  cargar()
  const [ua, ca] = await Promise.all([usuariosAPI.listar({}), contactosAPI.listar({})])
  agentes.value   = ua.data.results ?? ua.data
  contactos.value = ca.data.results ?? ca.data
})
</script>

<style scoped>
@import '../assets/crud.css';

.kanban-board   { display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 1rem; }
.kanban-col     { min-width: 200px; flex: 1; background: #f8f9fa; border-radius: 10px; padding: .75rem; }
.kanban-col-header { display: flex; justify-content: space-between; align-items: center;
                     border-top: 4px solid #ccc; padding-top: .5rem; margin-bottom: .75rem; }
.kanban-col-titulo { font-weight: 700; font-size: .85rem; color: #333; }
.kanban-badge   { background: #e9ecef; border-radius: 99px; padding: 2px 8px; font-size: .75rem; font-weight: 700; }
.kanban-cards   { display: flex; flex-direction: column; gap: .6rem; }
.kanban-card    { background: white; border-radius: 8px; padding: .75rem;
                  box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.kcard-titulo   { font-weight: 700; font-size: .85rem; margin-bottom: .3rem; }
.kcard-contacto { font-size: .78rem; color: #666; margin-bottom: .3rem; }
.kcard-monto    { font-size: .9rem; font-weight: 700; color: #1B6B3A; margin-bottom: .4rem; }
.kcard-prob     { display: flex; align-items: center; gap: .5rem; font-size: .75rem; margin-bottom: .4rem; }
.prob-bar       { flex: 1; height: 5px; background: #e9ecef; border-radius: 99px; overflow: hidden; }
.prob-fill      { height: 100%; border-radius: 99px; transition: width .3s; }
.kcard-acciones { display: flex; gap: .3rem; justify-content: flex-end; }
.btn-icon-sm    { background: none; border: 1px solid #dee2e6; border-radius: 5px;
                  padding: 2px 6px; cursor: pointer; font-size: .8rem; }
.btn-icon-sm:disabled { opacity: .3; cursor: not-allowed; }
.kanban-vacio   { text-align: center; font-size: .8rem; color: #aaa; padding: 1rem 0; }
</style>
