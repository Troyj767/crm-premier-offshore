#!/bin/bash
# ===========================================================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA - CRM Premier Offshore Solutions
# Sistema Operativo: Ubuntu 22.04 LTS
# Ejecutar como: sudo bash install.sh
# ===========================================================================

set -e  # Detener el script si cualquier comando falla

# ── Colores para output ──────────────────────────────────────────────────────
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
ROJO='\033[0;31m'
NC='\033[0m' # Sin color

ok()   { echo -e "${VERDE}[OK]${NC} $1"; }
info() { echo -e "${AMARILLO}[INFO]${NC} $1"; }
err()  { echo -e "${ROJO}[ERROR]${NC} $1"; exit 1; }

# ── Verificar que se ejecuta como root ──────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    err "Ejecuta este script como root: sudo bash install.sh"
fi

echo ""
echo "==========================================================="
echo "  CRM Premier Offshore Solutions - Instalación del Servidor"
echo "==========================================================="
echo ""

# ===========================================================================
# PASO 1: Actualizar el sistema
# ===========================================================================
info "Paso 1/8 - Actualizando paquetes del sistema..."
apt-get update -y && apt-get upgrade -y
ok "Sistema actualizado."

# ===========================================================================
# PASO 2: Instalar dependencias base
# ===========================================================================
info "Paso 2/8 - Instalando dependencias base..."
apt-get install -y \
    curl wget git unzip \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg lsb-release \
    ufw
ok "Dependencias base instaladas."

# ===========================================================================
# PASO 3: Instalar Python 3.11 y pip
# ===========================================================================
info "Paso 3/8 - Instalando Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -y
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version
ok "Python 3.11 instalado."

# Instalar bcrypt (para contraseñas)
pip3 install bcrypt
ok "bcrypt instalado."

# ===========================================================================
# PASO 4: Instalar MySQL 8.0
# ===========================================================================
info "Paso 4/8 - Instalando MySQL 8.0..."
apt-get install -y mysql-server mysql-client libmysqlclient-dev

# Iniciar y habilitar MySQL
systemctl start  mysql
systemctl enable mysql
ok "MySQL 8.0 instalado y en ejecución."

# Configurar base de datos y usuario
info "Configurando base de datos CRM..."
DB_NAME="CRM_PremierOffshore"
DB_USER="crm_user"
DB_PASS="CRM_Secure2024!"   # ← Cambia esta contraseña antes de ejecutar

mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
ok "Base de datos '${DB_NAME}' y usuario '${DB_USER}' creados."

# Cargar el script SQL del proyecto
if [ -f "/var/www/crm/database/CRM_PremierOffshore_DB.sql" ]; then
    mysql -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" < /var/www/crm/database/CRM_PremierOffshore_DB.sql
    ok "Script SQL ejecutado. Tablas y datos de prueba cargados."
else
    info "Archivo SQL no encontrado en /var/www/crm/database/. Cárgalo manualmente después."
fi

# ===========================================================================
# PASO 5: Instalar Nginx
# ===========================================================================
info "Paso 5/8 - Instalando Nginx..."
apt-get install -y nginx
systemctl start  nginx
systemctl enable nginx
ok "Nginx instalado y en ejecución."

# Copiar configuración del proyecto
if [ -f "/var/www/crm/nginx.conf" ]; then
    cp /var/www/crm/nginx.conf /etc/nginx/sites-available/crm
    ln -sf /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/crm
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx
    ok "Configuración de Nginx aplicada."
else
    info "nginx.conf no encontrado. Cópialo manualmente a /etc/nginx/sites-available/crm"
fi

# ===========================================================================
# PASO 6: Instalar Node.js 20 y construir el frontend
# ===========================================================================
info "Paso 6/8 - Instalando Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
node --version && npm --version
ok "Node.js instalado."

# Build del frontend Vue.js
if [ -d "/var/www/crm/frontend" ]; then
    info "Construyendo el frontend Vue.js..."
    cd /var/www/crm/frontend
    npm install
    npm run build
    ok "Frontend compilado en /var/www/crm/frontend/dist"
else
    info "Carpeta frontend no encontrada. Ejecuta 'npm install && npm run build' manualmente."
fi

# ===========================================================================
# PASO 7: Configurar el backend Django
# ===========================================================================
info "Paso 7/8 - Configurando el backend Django..."

BACKEND_DIR="/var/www/crm/backend"

if [ -d "$BACKEND_DIR" ]; then
    cd "$BACKEND_DIR"

    # Crear entorno virtual
    python3.11 -m venv venv
    source venv/bin/activate

    # Instalar dependencias Python
    pip install --upgrade pip
    pip install -r requirements.txt
    ok "Dependencias Python instaladas."

    # Copiar y configurar .env
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        cp /var/www/crm/.env.example "$BACKEND_DIR/.env"
        info "Archivo .env creado. EDÍTALO antes de continuar: nano $BACKEND_DIR/.env"
    fi

    # Aplicar migraciones
    python manage.py migrate
    ok "Migraciones de Django aplicadas."

    # Recolectar archivos estáticos
    python manage.py collectstatic --noinput
    ok "Archivos estáticos recolectados."

    deactivate
else
    info "Carpeta backend no encontrada en $BACKEND_DIR"
fi

# ── Crear servicio systemd para Gunicorn ─────────────────────────────────────
info "Creando servicio systemd para Gunicorn..."

cat > /etc/systemd/system/crm_gunicorn.service <<EOF
[Unit]
Description=Gunicorn - CRM Premier Offshore Solutions
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/crm/backend
EnvironmentFile=/var/www/crm/backend/.env
ExecStart=/var/www/crm/backend/venv/bin/gunicorn \\
    config.wsgi:application \\
    --bind 127.0.0.1:8000 \\
    --workers 3 \\
    --timeout 120 \\
    --access-logfile /var/log/crm_gunicorn_access.log \\
    --error-logfile  /var/log/crm_gunicorn_error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable crm_gunicorn
systemctl start  crm_gunicorn
ok "Servicio Gunicorn creado y en ejecución."

# ===========================================================================
# PASO 8: Configurar Firewall (UFW)
# ===========================================================================
info "Paso 8/8 - Configurando Firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'   # Permite puertos 80 y 443
ufw --force enable
ok "Firewall configurado. Puertos 22 (SSH), 80 (HTTP) y 443 (HTTPS) abiertos."

# ===========================================================================
# RESUMEN FINAL
# ===========================================================================
IP_LOCAL=$(hostname -I | awk '{print $1}')

echo ""
echo "==========================================================="
echo -e "${VERDE}  INSTALACIÓN COMPLETADA${NC}"
echo "==========================================================="
echo ""
echo "  El sistema CRM está disponible en:"
echo -e "  ${VERDE}→ http://${IP_LOCAL}${NC}"
echo ""
echo "  Servicios activos:"
echo "    • Nginx      : $(systemctl is-active nginx)"
echo "    • MySQL      : $(systemctl is-active mysql)"
echo "    • Gunicorn   : $(systemctl is-active crm_gunicorn)"
echo ""
echo "  Logs útiles:"
echo "    • Nginx:    tail -f /var/log/nginx/crm_error.log"
echo "    • Gunicorn: tail -f /var/log/crm_gunicorn_error.log"
echo ""
echo "  Próximos pasos:"
echo "    1. Edita el archivo .env:  nano /var/www/crm/backend/.env"
echo "    2. Reinicia Gunicorn:      sudo systemctl restart crm_gunicorn"
echo "    3. Crea el superusuario:   cd /var/www/crm/backend && source venv/bin/activate && python manage.py createsuperuser"
echo ""
echo "==========================================================="
