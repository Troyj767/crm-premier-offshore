<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-sub">Resumen del sistema — {{ fechaHoy }}</p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid" v-if="!cargando">
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#d6ecd2">👥</div>
        <div class="kpi-info">
          <span class="kpi-valor">{{ kpis.contactos_activos }}</span>
          <span class="kpi-label">Contactos activos</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#cfe2ff">🆕</div>
        <div class="kpi-info">
          <span class="kpi-valor">{{ kpis.contactos_nuevos_mes }}</span>
          <span class="kpi-label">Nuevos este mes</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#ffe5cc">✅</div>
        <div class="kpi-info">
          <span class="kpi-valor">{{ kpis.tareas_pendientes }}</span>
          <span class="kpi-label">Tareas pendientes</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#f8d7da">⚠️</div>
        <div class="kpi-info">
          <span class="kpi-valor kpi-rojo">{{ kpis.tareas_vencidas }}</span>
          <span class="kpi-label">Tareas vencidas</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#e2d9f3">📞</div>
        <div class="kpi-info">
          <span class="kpi-valor">{{ kpis.interacciones_mes }}</span>
          <span class="kpi-label">Interacciones este mes</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background:#d6ecd2">📈</div>
        <div class="kpi-info">
          <span class="kpi-valor">{{ kpis.tasa_conversion_pct }}%</span>
          <span class="kpi-label">Tasa de conversión</span>
        </div>
      </div>
    </div>

    <!-- Pipeline por etapa -->
    <div class="seccion" v-if="!cargando">
      <h2 class="seccion-titulo">Pipeline por Etapa</h2>
      <div class="pipeline-tabla">
        <div class="pipeline-fila encabezado">
          <span>Etapa</span><span>Oportunidades</span><span>Valor Total</span>
        </div>
        <div
          v-for="e in kpis.pipeline_por_etapa"
          :key="e.etapa"
          class="pipeline-fila"
        >
          <span class="etapa-nombre">{{ e.etapa }}</span>
          <span class="badge badge-azul">{{ e.total }}</span>
          <span class="valor-monto">${{ Number(e.valor || 0).toLocaleString('es-DO') }}</span>
        </div>
        <div v-if="!kpis.pipeline_por_etapa?.length" class="sin-datos">Sin datos de pipeline.</div>
      </div>
    </div>

    <div v-if="cargando" class="estado-carga">Cargando dashboard...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardAPI } from '../services/api.js'

const kpis     = ref({})
const cargando = ref(true)
const fechaHoy = new Date().toLocaleDateString('es-DO', { dateStyle: 'full' })

onMounted(async () => {
  try {
    const res = await dashboardAPI.kpis()
    kpis.value = res.data
  } finally { cargando.value = false }
})
</script>

<style scoped>
@import '../assets/crud.css';

.kpi-grid       { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                  gap: 1rem; margin-bottom: 2rem; }
.kpi-card       { background: white; border-radius: 12px; padding: 1.2rem;
                  display: flex; align-items: center; gap: 1rem;
                  box-shadow: 0 2px 12px rgba(0,0,0,.07); }
.kpi-icon       { width: 48px; height: 48px; border-radius: 12px;
                  display: flex; align-items: center; justify-content: center;
                  font-size: 1.4rem; flex-shrink: 0; }
.kpi-info       { display: flex; flex-direction: column; }
.kpi-valor      { font-size: 1.8rem; font-weight: 800; color: #1B6B3A; line-height: 1; }
.kpi-rojo       { color: #dc3545; }
.kpi-label      { font-size: .78rem; color: #6c757d; margin-top: .2rem; }

.seccion        { background: white; border-radius: 12px; padding: 1.5rem;
                  box-shadow: 0 2px 12px rgba(0,0,0,.07); }
.seccion-titulo { font-size: 1.1rem; font-weight: 700; color: #1B6B3A; margin: 0 0 1rem; }
.pipeline-tabla { display: flex; flex-direction: column; gap: .4rem; }
.pipeline-fila  { display: grid; grid-template-columns: 1fr 140px 160px;
                  padding: .6rem .75rem; border-radius: 8px; align-items: center; }
.encabezado     { background: #f8f9fa; font-size: .78rem; font-weight: 700;
                  color: #6c757d; text-transform: uppercase; }
.pipeline-fila:not(.encabezado):hover { background: #f8f9fa; }
.etapa-nombre   { font-weight: 600; }
.valor-monto    { font-weight: 700; color: #1B6B3A; }
</style>
