# backend/crm/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles',         views.RolViewSet)
router.register(r'usuarios',      views.UsuarioViewSet)
router.register(r'contactos',     views.ContactoViewSet)
router.register(r'interacciones', views.InteraccionViewSet)
router.register(r'oportunidades', views.OportunidadViewSet)
router.register(r'tareas',        views.TareaViewSet)
router.register(r'auditoria',     views.LogAuditoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_kpis, name='dashboard-kpis'),
]
