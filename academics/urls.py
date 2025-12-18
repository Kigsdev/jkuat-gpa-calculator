from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('transcript/', views.TranscriptView.as_view(), name='transcript'),
    path('units/', views.UnitsView.as_view(), name='units'),
    path('projection/', views.ProjectionView.as_view(), name='projection'),
]
