from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('habitos/', views.registro_habitos, name='habitos'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path("estadistica/", views.estadistica_view, name="estadistica"),
    path("recursos/", views.recursos_view, name="recursos"),
    path("diario/", views.diario, name="diario"),
]
