#Routing
from app import views
from app.fichas_viewsets import (
    HogarViewSet, CargaFamiliarViewSet, InformacionSaludViewSet,
    RedConocidaViewSet, RegistroSocialViewSet, AnotacionesHogarViewSet
)
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

router = routers.DefaultRouter()

# CRUD de Clientes y Asuntos
router.register(r'clientes', views.ClientesViewSet)
router.register(r'asuntos', views.AsuntoViewSet)
router.register(r'registros-asuntos', views.RegistroAsuntoViewSet)
router.register(r'asistencias', views.AsistenciaViewSet)

# CRUD de Fichas Sociales
router.register(r'hogar', HogarViewSet)
router.register(r'carga-familiar', CargaFamiliarViewSet)
router.register(r'informacion-salud', InformacionSaludViewSet)
router.register(r'redes', RedConocidaViewSet)
router.register(r'registro-social', RegistroSocialViewSet)
router.register(r'anotaciones', AnotacionesHogarViewSet)

urlpatterns = [
    # Rutas manuales ANTES que el router (para que tengan prioridad)
    path('api/v1/clientes/upload-excel/', views.UploadExcelView.as_view(), name='upload-excel'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Router DESPUÉS de las rutas manuales
    path('api/v1/', include(router.urls)),
]
