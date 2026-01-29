from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('update/', views.update_stats_view, name='update_stats'),
    path('report/', views.generate_report_view, name='generate_report'),
    # Dashboard - główna strona ze statystykami
    path('', views.dashboard_view, name='dashboard'),
]