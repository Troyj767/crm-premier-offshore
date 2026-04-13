# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from crm.auth import LoginView, LogoutView

urlpatterns = [
    # ── Panel de administración Django ────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Autenticación JWT ─────────────────────────────────────────────────────
    path('api/auth/token/',         LoginView.as_view(),        name='token-login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/logout/',        LogoutView.as_view(),       name='token-logout'),

    # ── API principal del CRM ─────────────────────────────────────────────────
    path('api/', include('crm.urls')),
]

# Servir media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
