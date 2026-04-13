import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Interceptor: lee el token en CADA request (no al crear la instancia)
api.interceptors.request.use(config => {
  const token     = localStorage.getItem('access_token')
  const usuarioId = localStorage.getItem('usuario_id')
  if (token)     config.headers['Authorization']  = `Bearer ${token}`
  if (usuarioId) config.headers['X-Usuario-Id']   = usuarioId
  return config
})

api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export const contactosAPI = {
  listar:   (params) => api.get('/contactos/',       { params }),
  obtener:  (id)     => api.get(`/contactos/${id}/`),
  crear:    (data)   => api.post('/contactos/',      data),
  editar:   (id, d)  => api.put(`/contactos/${id}/`, d),
  eliminar: (id)     => api.delete(`/contactos/${id}/`),
  historial:(id)     => api.get(`/contactos/${id}/historial/`),
  pipeline: (id)     => api.get(`/contactos/${id}/pipeline/`),
}

export const interaccionesAPI = {
  listar:   (params) => api.get('/interacciones/',       { params }),
  obtener:  (id)     => api.get(`/interacciones/${id}/`),
  crear:    (data)   => api.post('/interacciones/',      data),
  editar:   (id, d)  => api.put(`/interacciones/${id}/`, d),
  eliminar: (id)     => api.delete(`/interacciones/${id}/`),
}

export const oportunidadesAPI = {
  listar:   (params) => api.get('/oportunidades/',       { params }),
  obtener:  (id)     => api.get(`/oportunidades/${id}/`),
  crear:    (data)   => api.post('/oportunidades/',      data),
  editar:   (id, d)  => api.put(`/oportunidades/${id}/`, d),
  eliminar: (id)     => api.delete(`/oportunidades/${id}/`),
  porEtapa: ()       => api.get('/oportunidades/por_etapa/'),
}

export const tareasAPI = {
  listar:   (params) => api.get('/tareas/',       { params }),
  obtener:  (id)     => api.get(`/tareas/${id}/`),
  crear:    (data)   => api.post('/tareas/',      data),
  editar:   (id, d)  => api.put(`/tareas/${id}/`, d),
  eliminar: (id)     => api.delete(`/tareas/${id}/`),
  urgentes: ()       => api.get('/tareas/urgentes/'),
}

export const usuariosAPI = {
  listar:   (params) => api.get('/usuarios/',       { params }),
  obtener:  (id)     => api.get(`/usuarios/${id}/`),
  crear:    (data)   => api.post('/usuarios/',      data),
  editar:   (id, d)  => api.put(`/usuarios/${id}/`, d),
  eliminar: (id)     => api.delete(`/usuarios/${id}/`),
}

export const auditoriaAPI = {
  listar: (params) => api.get('/auditoria/', { params }),
}

export const dashboardAPI = {
  kpis: () => api.get('/dashboard/'),
}

export default api