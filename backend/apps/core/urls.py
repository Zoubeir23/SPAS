"""
Core URL configuration.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/reset/', views.reset_settings, name='reset_settings'),
]
