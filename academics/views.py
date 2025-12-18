from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Result, Student
from .utils import GradeCalculator


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard showing student's academic summary."""
    template_name = 'academics/dashboard.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            gpa_data = GradeCalculator.calculate_wma(student)
            grade_dist = GradeCalculator.get_grade_distribution(student)
            
            context['student'] = student
            context['gpa'] = gpa_data['gpa']
            context['honors'] = gpa_data['honors_level']
            context['units_completed'] = gpa_data['units_completed']
            context['failed_units'] = gpa_data['failed_units']
            context['grade_distribution'] = grade_dist
        except Student.DoesNotExist:
            context['student'] = None
        
        return context


class TranscriptView(LoginRequiredMixin, TemplateView):
    """Display student's academic transcript."""
    template_name = 'academics/transcript.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            transcript = GradeCalculator.get_transcript(student)
            gpa_data = GradeCalculator.calculate_wma(student)
            
            context['student'] = student
            context['transcript'] = transcript
            context['gpa'] = gpa_data['gpa']
            context['total_points'] = gpa_data['total_points']
            context['total_credit_units'] = gpa_data['total_credit_units']
        except Student.DoesNotExist:
            context['student'] = None
        
        return context


class UnitsView(LoginRequiredMixin, TemplateView):
    """Display available units and results."""
    template_name = 'academics/units.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            results = Result.objects.filter(student=student).select_related('unit')
            context['student'] = student
            context['results'] = results
        except Student.DoesNotExist:
            context['student'] = None
        
        return context


class ProjectionView(LoginRequiredMixin, TemplateView):
    """Graduation planner - project future grades needed."""
    template_name = 'academics/projection.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            gpa_data = GradeCalculator.calculate_wma(student)
            
            # Projection targets
            targets = [
                {'name': 'First Class Honours', 'gpa': 70},
                {'name': 'Second Class (Upper)', 'gpa': 60},
                {'name': 'Second Class (Lower)', 'gpa': 50},
            ]
            
            projections = []
            for target in targets:
                projection = GradeCalculator.project_required_average(
                    student,
                    target['gpa'],
                    remaining_units=8  # Default remaining units - can be customized
                )
                projection['target_name'] = target['name']
                projections.append(projection)
            
            context['student'] = student
            context['current_gpa'] = gpa_data['gpa']
            context['projections'] = projections
        except Student.DoesNotExist:
            context['student'] = None
        
        return context

