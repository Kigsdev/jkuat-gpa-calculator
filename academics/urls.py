from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('transcript/', views.TranscriptView.as_view(), name='transcript'),
    path('units/', views.UnitsView.as_view(), name='units'),
    path('projection/', views.ProjectionView.as_view(), name='projection'),
    
    # Phase 5: Advanced Features
    path('transcript/export/', views.TranscriptPDFExportView.as_view(), name='transcript_export'),
    path('projection/export/', views.ProjectionPDFExportView.as_view(), name='projection_export'),
    path('analytics/', views.GradeAnalyticsView.as_view(), name='analytics'),
    path('notifications/settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    path('alerts/', views.GradeAlertsListView.as_view(), name='alerts'),
    path('alerts/<int:alert_id>/mark-read/', views.MarkAlertAsReadView.as_view(), name='mark_alert_read'),
]
