"""
URL configuration for Alert app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, InterventionViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'interventions', InterventionViewSet, basename='intervention')

urlpatterns = [
    path('', include(router.urls)),
]
