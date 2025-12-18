from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
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
            context['gpa'] = f"{gpa_data.get('gpa', 0.00):.2f}"
            context['honors'] = gpa_data.get('honors_level', 'Pass')
            context['units_completed'] = gpa_data.get('units_completed', 0)
            context['failed_units'] = gpa_data.get('failed_units', 0)
            context['grade_distribution'] = grade_dist
            context['total_points'] = gpa_data.get('total_points', 0)
            context['total_credit_units'] = gpa_data.get('total_credit_units', 0)
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found. Please contact the registrar.'
            context['student'] = None
        except Exception as e:
            context['error'] = f'Error loading dashboard: {str(e)}'
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
            context['gpa'] = f"{gpa_data.get('gpa', 0.00):.2f}"
            context['total_points'] = gpa_data.get('total_points', 0)
            context['total_credit_units'] = gpa_data.get('total_credit_units', 0)
            context['honors_level'] = gpa_data.get('honors_level', 'Pass')
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found. Please contact the registrar.'
            context['student'] = None
        except Exception as e:
            context['error'] = f'Error loading transcript: {str(e)}'
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
            results = Result.objects.filter(
                student=student
            ).select_related('unit').order_by('unit__code')
            
            context['student'] = student
            context['results'] = results
            context['total_units'] = results.count()
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found. Please contact the registrar.'
            context['student'] = None
            context['results'] = []
        except Exception as e:
            context['error'] = f'Error loading units: {str(e)}'
            context['student'] = None
            context['results'] = []
        
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
            current_gpa = gpa_data.get('gpa', 0.00)
            
            # Projection targets for different honor levels
            targets = {
                'First Class Honours': 70.0,
                'Second Class (Upper)': 60.0,
                'Second Class (Lower)': 50.0,
                'Pass': 40.0,
            }
            
            projections = {}
            remaining_units = 8  # Default - can be customized
            
            for target_name, target_gpa in targets.items():
                projection = GradeCalculator.project_required_average(
                    student,
                    target_gpa,
                    remaining_units=remaining_units
                )
                projections[target_name] = projection
            
            context['student'] = student
            context['current_gpa'] = f"{current_gpa:.2f}"
            context['projections'] = projections
            context['remaining_units'] = remaining_units
            context['honors_level'] = gpa_data.get('honors_level', 'Pass')
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found. Please contact the registrar.'
            context['student'] = None
            context['projections'] = {}
        except Exception as e:
            context['error'] = f'Error loading projections: {str(e)}'
            context['student'] = None
            context['projections'] = {}
        
        return context

