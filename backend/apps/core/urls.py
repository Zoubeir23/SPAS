"""
Core URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core'

router = DefaultRouter()
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/reset/', views.reset_settings, name='reset_settings'),
    path('', include(router.urls)),
]
