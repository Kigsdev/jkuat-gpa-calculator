from django.contrib import admin
from .models import AcademicYear, Unit, Result, GPACalculation


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active', 'created_at']
    list_filter = ['is_active', 'year', 'semester']
    list_editable = ['is_active']
    ordering = ['-year', '-semester']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credit_units', 'academic_year']
    search_fields = ['code', 'name']
    list_filter = ['academic_year', 'credit_units']
    ordering = ['code']
    fieldsets = (
        ('Unit Information', {
            'fields': ('code', 'name', 'credit_units')
        }),
        ('Academic Year', {
            'fields': ('academic_year',)
        }),
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'unit', 'score', 'grade', 'points']
    search_fields = ['student__user__username', 'student__registration_number', 'unit__code']
    list_filter = ['grade', 'unit__academic_year', 'created_at']
    readonly_fields = ['grade', 'points', 'created_at', 'updated_at']
    fieldsets = (
        ('Student & Unit', {
            'fields': ('student', 'unit')
        }),
        ('Score Information', {
            'fields': ('score', 'grade', 'points')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GPACalculation)
class GPACalculationAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'gpa', 'total_credit_units', 'calculated_at']
    search_fields = ['student__user__username', 'student__registration_number']
    list_filter = ['academic_year', 'calculated_at']
    readonly_fields = ['calculated_at', 'gpa', 'total_points', 'total_credit_units']
    fieldsets = (
        ('Student & Academic Year', {
            'fields': ('student', 'academic_year')
        }),
        ('GPA Information', {
            'fields': ('gpa', 'total_points', 'total_credit_units')
        }),
        ('Calculation Time', {
            'fields': ('calculated_at',),
            'classes': ('collapse',)
        }),
    )

