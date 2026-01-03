"""
Analytics URL Configuration
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/', views.dashboard_stats, name='dashboard'),
    path('metrics/', views.analytics_metrics, name='metrics'),
    
    # Distribution and evolution
    path('risk-distribution/', views.risk_distribution, name='risk-distribution'),
    path('dropout-evolution/', views.dropout_evolution, name='dropout-evolution'),
    
    # Performance metrics
    path('program-performance/', views.program_performance, name='program-performance'),
    path('intervention-efficacy/', views.intervention_efficacy, name='intervention-efficacy'),
    path('model-performance/', views.model_performance_history, name='model-performance'),
    
    # Student-specific analytics
    path('prediction-factors/<uuid:student_id>/', views.prediction_factors, name='prediction-factors'),
    path('risk-evolution/<uuid:student_id>/', views.risk_evolution, name='risk-evolution'),
]
