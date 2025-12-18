from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'user', 'course', 'year_of_study', 'academic_year']
    search_fields = ['registration_number', 'user__username', 'user__first_name', 'user__last_name']
    list_filter = ['year_of_study', 'academic_year', 'created_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Details', {
            'fields': ('registration_number', 'course', 'year_of_study', 'academic_year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

