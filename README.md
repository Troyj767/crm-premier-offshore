[README.md](https://github.com/user-attachments/files/26688312/README.md)
# 🏢 CRM Premier Offshore Solutions

![Estado](https://img.shields.io/badge/Estado-Funcional-brightgreen)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![BD](https://img.shields.io/badge/BD-MySQL%208.0-blue)
![Backend](https://img.shields.io/badge/Backend-Django%204.2-092E20)
![Frontend](https://img.shields.io/badge/Frontend-Vue.js%203-42b883)
![Docker](https://img.shields.io/badge/Docker-Listo-2496ED)

Sistema de Gestión de Clientes (CRM) desarrollado para **Premier Offshore Solutions**, empresa dominicana de servicios de contact center bilingüe. Proyecto académico de la asignatura **Desarrollo de Proyectos con Software Libre** — Universidad Abierta para Adultos (UAPA).

---

## 📌 Descripción

Premier Offshore Solutions requería una herramienta centralizada para gestionar clientes empresariales, automatizar el seguimiento de interacciones y generar reportes de rendimiento para su equipo de agentes bilingües. Este CRM fue desarrollado **100% con software libre**.

---

## ✅ Funcionalidades

| Módulo | Descripción | RF |
|---|---|---|
| **Gestión de Contactos** | CRUD completo con filtros por nombre, empresa y estado | RF-01, RF-02 |
| **Importación CSV** | Importar contactos desde archivos CSV/Excel | RF-03 |
| **Seguimiento de Interacciones** | Registro de llamadas, correos y chats con historial | RF-04, RF-05 |
| **Pipeline de Ventas** | Tablero Kanban con etapas del ciclo de ventas | RF-06, RF-07 |
| **Gestión de Tareas** | Creación y asignación con prioridad y fecha límite | RF-08 |
| **Notificaciones** | Alertas por tareas vencidas o próximas a vencer | RF-09 |
| **Dashboard KPIs** | Tasa de conversión, contactos nuevos, tareas pendientes | RF-10, RF-11 |
| **Control de Acceso** | Roles: Agente, Supervisor, Administrador | RF-12 |
| **Auditoría** | Log de acciones con IP y valores anterior/nuevo | RF-13 |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Licencia |
|---|---|---|
| Frontend | Vue.js 3 + Tailwind CSS | MIT |
| Backend | Python 3.11 + Django REST Framework | MIT / BSD |
| Autenticación | JWT custom (djangorestframework-simplejwt) | MIT |
| Base de Datos | MySQL 8.0 | GPL v2 |
| Servidor Web | Nginx + Gunicorn | BSD / MIT |
| Contenedores | Docker + Docker Compose | Apache 2.0 |
| Control de Versiones | Git + GitHub | MIT |
| Gestión del Proyecto | GanttProject | GPL v3 |

---

## 📁 Estructura del Proyecto

```
crm-premier-offshore/
├── backend/
│   ├── config/settings.py          # Configuración Django
│   ├── config/urls.py              # URLs raíz
│   ├── crm/models.py               # Modelos de datos
│   ├── crm/views.py                # CRUD ViewSets + Dashboard
│   ├── crm/auth.py                 # Login/Logout JWT
│   ├── crm/authentication.py       # Backend JWT custom
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/views/                  # Dashboard, Contactos, Pipeline, Tareas...
│   ├── src/services/api.js         # Servicio API centralizado
│   ├── src/App.vue                 # Layout con sidebar
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── CRM_PremierOffshore_DB.sql  # Esquema + datos de prueba
├── docker-compose.yml
├── nginx.conf
├── install.sh                      # Script instalación Linux automática
└── README.md
```

---

## ⚙️ Instalación Rápida con Docker (Windows/Mac/Linux)

### Prerrequisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Troyj767/crm-premier-offshore.git
cd crm-premier-offshore

# 2. Crear archivo de configuración
cp .env.example .env

# 3. Levantar todos los servicios (primera vez: 5-10 min)
docker-compose up --build

# 4. En OTRA ventana: cargar usuarios de prueba
docker exec crm_backend python manage.py shell -c "
from crm.models import Rol, Usuario
import bcrypt
r1,_=Rol.objects.get_or_create(nombre_rol='Agente',defaults={'descripcion':'Cartera propia'})
r2,_=Rol.objects.get_or_create(nombre_rol='Supervisor',defaults={'descripcion':'Su equipo'})
r3,_=Rol.objects.get_or_create(nombre_rol='Administrador',defaults={'descripcion':'Total'})
h=bcrypt.hashpw(b'demo1234',bcrypt.gensalt()).decode()
Usuario.objects.get_or_create(correo='mvaldez@premieroffshore.com',defaults={'nombre':'Marcos Valdez','contrasena_hash':h,'id_rol':r3})
Usuario.objects.get_or_create(correo='drosario@premieroffshore.com',defaults={'nombre':'Daniela Rosario','contrasena_hash':h,'id_rol':r2})
Usuario.objects.get_or_create(correo='jcastillo@premieroffshore.com',defaults={'nombre':'Javier Castillo','contrasena_hash':h,'id_rol':r1})
print('OK')
"
```

**Acceder:** http://localhost:8080

### Variables de Entorno (`.env`)

```env
DB_NAME=CRM_PremierOffshore
DB_USER=crm_user
DB_PASSWORD=crm1234
DB_ROOT_PASSWORD=root1234
DB_HOST=db
DB_PORT=3306
SECRET_KEY=clave-secreta-para-el-crm-premier-2024
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7
VITE_API_URL=http://localhost:8080/api
```

---

## 🖥️ Instalación en Servidor Linux (Producción)

```bash
# Clonar el proyecto
git clone https://github.com/Troyj767/crm-premier-offshore.git /var/www/crm

# Ejecutar el script de instalación automática
chmod +x /var/www/crm/install.sh
sudo bash /var/www/crm/install.sh
```

Instala automáticamente: Python 3.11, MySQL 8.0, Nginx, Node.js, Gunicorn y configura el firewall.

> 📄 Ver guía detallada en `/docs/Guia_Despliegue_Servidor_CRM.docx`

---

## 🗄️ Base de Datos

```bash
# Cargar esquema manualmente
mysql -u crm_user -p CRM_PremierOffshore < database/CRM_PremierOffshore_DB.sql
```

---

## 🖥️ Credenciales de Prueba

| Usuario | Correo | Contraseña | Rol |
|---|---|---|---|
| Marcos Valdez | mvaldez@premieroffshore.com | demo1234 | Administrador |
| Daniela Rosario | drosario@premieroffshore.com | demo1234 | Supervisor |
| Javier Castillo | jcastillo@premieroffshore.com | demo1234 | Agente |

---

## 👥 Equipo

| Nombre | Rol | Universidad |
|---|---|---|
| Erasmo | Desarrollador Full-Stack | UAPA |

**Empresa cliente:** Premier Offshore Solutions — Santiago de los Caballeros, República Dominicana.

**Asignatura:** Desarrollo de Proyectos con Software Libre — UAPA, Escuela de Ingeniería y Tecnología.

---

## 📄 Licencia

Proyecto académico bajo los principios del software libre. Todas las tecnologías son open source.
