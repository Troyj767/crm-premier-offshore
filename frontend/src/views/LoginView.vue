<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="panel-content">
        <div class="panel-logo">🏢</div>
        <h1 class="panel-titulo">Premier Offshore<br><strong>CRM</strong></h1>
        <p class="panel-sub">Sistema de Gestión de Clientes</p>
        <div class="panel-features">
          <div class="feature"><span>👥</span> Gestión de contactos y prospectos</div>
          <div class="feature"><span>📈</span> Pipeline de ventas Kanban</div>
          <div class="feature"><span>✅</span> Tareas y seguimiento</div>
          <div class="feature"><span>📊</span> Dashboard con KPIs en tiempo real</div>
        </div>
      </div>
      <div class="panel-footer">
        Universidad Abierta para Adultos — UAPA<br>
        Desarrollo de Proyectos con Software Libre
      </div>
    </div>

    <div class="login-form-wrap">
      <div class="login-card">
        <h2 class="form-titulo">Iniciar Sesión</h2>
        <p class="form-sub">Ingresa tus credenciales para acceder al sistema</p>

        <div v-if="error" class="alerta-error">
          ⚠️ {{ error }}
        </div>

        <form @submit.prevent="iniciarSesion" class="form">
          <div class="campo">
            <label for="correo">Correo electrónico</label>
            <div class="input-wrap">
              <span class="input-icono">✉️</span>
              <input id="correo" v-model="form.correo" type="email"
                placeholder="usuario@premieroffshore.com" required autocomplete="email"/>
            </div>
          </div>
          <div class="campo">
            <label for="contrasena">Contraseña</label>
            <div class="input-wrap">
              <span class="input-icono">🔒</span>
              <input id="contrasena" v-model="form.contrasena"
                :type="mostrarPass ? 'text' : 'password'"
                placeholder="••••••••" required autocomplete="current-password"/>
              <button type="button" class="toggle-pass" @click="mostrarPass = !mostrarPass">
                {{ mostrarPass ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>
          <button type="submit" class="btn-login" :disabled="cargando">
            <span v-if="cargando" class="spinner"></span>
            {{ cargando ? 'Verificando...' : 'Entrar al sistema' }}
          </button>
        </form>

        <div class="creds-demo">
          <p class="creds-titulo">Credenciales de prueba:</p>
          <div class="creds-grid">
            <div class="cred-item" @click="usarCred('mvaldez@premieroffshore.com')">
              <span class="cred-rol admin">Admin</span>
              <span>mvaldez@premieroffshore.com</span>
            </div>
            <div class="cred-item" @click="usarCred('drosario@premieroffshore.com')">
              <span class="cred-rol super">Supervisor</span>
              <span>drosario@premieroffshore.com</span>
            </div>
            <div class="cred-item" @click="usarCred('jcastillo@premieroffshore.com')">
              <span class="cred-rol agente">Agente</span>
              <span>jcastillo@premieroffshore.com</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api.js'

const cargando    = ref(false)
const error       = ref('')
const mostrarPass = ref(false)
const form        = ref({ correo: '', contrasena: '' })

async function iniciarSesion() {
  cargando.value = true
  error.value    = ''
  try {
    const res = await api.post('/auth/token/', {
      correo:     form.value.correo,
      contrasena: form.value.contrasena,
    })

    const { access, refresh, usuario } = res.data

    localStorage.setItem('access_token',  access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('usuario_id',    String(usuario.id))
    localStorage.setItem('usuario',       JSON.stringify(usuario))

    // Reload completo — garantiza que App.vue lea el token desde cero
    window.location.replace('/dashboard')

  } catch (err) {
    if (err.response?.status === 401) {
      error.value = 'Correo o contraseña incorrectos.'
    } else {
      error.value = 'No se pudo conectar al servidor. Intenta de nuevo.'
    }
  } finally {
    cargando.value = false
  }
}

function usarCred(correo) {
  form.value.correo     = correo
  form.value.contrasena = 'demo1234'
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

/* ── Panel izquierdo verde ──────────────────────────────────────────────── */
.login-panel {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #1B6B3A 0%, #0f4023 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 3rem 2.5rem;
  color: white;
}
.panel-content  { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 1.5rem; }
.panel-logo     { font-size: 3rem; }
.panel-titulo   { font-size: 1.9rem; line-height: 1.2; font-weight: 400; }
.panel-titulo strong { font-size: 2.2rem; }
.panel-sub      { color: rgba(255,255,255,.65); font-size: .95rem; }
.panel-features { display: flex; flex-direction: column; gap: .75rem; margin-top: .5rem; }
.feature        { display: flex; align-items: center; gap: .75rem;
                  font-size: .9rem; color: rgba(255,255,255,.85); }
.feature span   { font-size: 1.1rem; }
.panel-footer   { font-size: .75rem; color: rgba(255,255,255,.45); line-height: 1.5; }

/* ── Panel derecho: formulario ──────────────────────────────────────────── */
.login-form-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.login-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
}
.form-titulo { font-size: 1.5rem; font-weight: 800; color: #1B6B3A; margin-bottom: .3rem; }
.form-sub    { color: #6c757d; font-size: .88rem; margin-bottom: 1.5rem; }

.alerta-error {
  background: #fee2e2; border: 1px solid #fca5a5;
  border-radius: 8px; padding: .75rem 1rem;
  color: #dc2626; font-size: .88rem; margin-bottom: 1rem;
}

.form      { display: flex; flex-direction: column; gap: 1.1rem; }
.campo     { display: flex; flex-direction: column; gap: .35rem; }
.campo label { font-size: .82rem; font-weight: 600; color: #374151; }

.input-wrap {
  display: flex;
  align-items: center;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color .2s;
}
.input-wrap:focus-within { border-color: #1B6B3A; box-shadow: 0 0 0 3px rgba(27,107,58,.1); }
.input-icono { padding: 0 .75rem; font-size: 1rem; color: #9ca3af; }
.input-wrap input {
  flex: 1; border: none; outline: none;
  padding: .65rem .5rem .65rem 0;
  font-size: .92rem; color: #111;
  background: transparent;
}
.toggle-pass {
  background: none; border: none; padding: 0 .75rem;
  cursor: pointer; font-size: 1rem;
}

.btn-login {
  background: #1B6B3A; color: white; border: none;
  padding: .75rem; border-radius: 8px;
  font-size: .95rem; font-weight: 700;
  cursor: pointer; margin-top: .5rem;
  transition: opacity .2s;
  display: flex; align-items: center; justify-content: center; gap: .5rem;
}
.btn-login:hover    { opacity: .88; }
.btn-login:disabled { opacity: .6; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Credenciales demo ────────────────────────────────────────────────── */
.creds-demo  { margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid #f0f0f0; }
.creds-titulo { font-size: .75rem; font-weight: 700; color: #9ca3af;
                text-transform: uppercase; letter-spacing: .06em; margin-bottom: .6rem; }
.creds-grid  { display: flex; flex-direction: column; gap: .4rem; }
.cred-item   {
  display: flex; align-items: center; gap: .6rem;
  padding: .45rem .6rem; border-radius: 6px; cursor: pointer;
  font-size: .8rem; color: #555; border: 1px solid #f0f0f0;
  transition: background .15s;
}
.cred-item:hover { background: #f9fffe; border-color: #d6ecd2; }
.cred-rol    { font-size: .7rem; font-weight: 700; border-radius: 99px;
               padding: 2px 8px; flex-shrink: 0; }
.admin  { background: #d6ecd2; color: #1B6B3A; }
.super  { background: #cfe2ff; color: #0a58ca; }
.agente { background: #e9ecef; color: #495057; }

@media (max-width: 768px) {
  .login-panel { display: none; }
}
</style>
