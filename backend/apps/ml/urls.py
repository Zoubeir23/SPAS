"""
URL configuration for ML app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MLModelViewSet, TrainingJobViewSet, PredictionViewSet

router = DefaultRouter()
router.register(r'models', MLModelViewSet, basename='ml-model')
router.register(r'training-jobs', TrainingJobViewSet, basename='training-job')
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
]
