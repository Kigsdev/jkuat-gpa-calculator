from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from .models import Result, Student, NotificationPreference, GradeAlert, GradeAnalytics
from .utils import GradeCalculator, PDFGenerator, AnalyticsCalculator


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


# ========== Phase 5 Views: Advanced Features ==========

class TranscriptPDFExportView(LoginRequiredMixin, View):
    """Export academic transcript as PDF."""
    login_url = 'accounts:login'
    
    def get(self, request):
        try:
            student = request.user.student
            gpa_data = GradeCalculator.calculate_wma(student)
            
            # Generate PDF
            pdf_bytes = PDFGenerator.generate_transcript_pdf(student, gpa_data)
            
            # Return as download
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transcript_{student.registration_number}.pdf"'
            return response
        except ObjectDoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('academics:dashboard')
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('academics:transcript')


class GradeAnalyticsView(LoginRequiredMixin, TemplateView):
    """Display grade analytics and insights."""
    template_name = 'academics/analytics.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            
            # Calculate analytics
            analytics = AnalyticsCalculator.calculate_analytics(student)
            gpa_data = GradeCalculator.calculate_wma(student)
            alerts = AnalyticsCalculator.check_grade_alerts(student, gpa_data)
            
            # Get or create analytics record
            grade_analytics, _ = GradeAnalytics.objects.get_or_create(student=student)
            grade_analytics.average_grade_score = analytics['average_score']
            grade_analytics.best_performing_unit = analytics['best_unit'] or ''
            grade_analytics.worst_performing_unit = analytics['worst_unit'] or ''
            grade_analytics.units_at_risk = analytics['units_at_risk']
            grade_analytics.gpa_trend = analytics['gpa_trend']
            grade_analytics.save()
            
            context['student'] = student
            context['analytics'] = analytics
            context['gpa'] = f"{gpa_data.get('gpa', 0):.2f}"
            context['alerts'] = alerts
            context['trend_icon'] = {
                'improving': '📈',
                'declining': '📉',
                'stable': '➡️'
            }.get(analytics['gpa_trend'], '➡️')
            
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found.'
            context['student'] = None
        except Exception as e:
            context['error'] = f'Error loading analytics: {str(e)}'
            context['student'] = None
        
        return context


class NotificationSettingsView(LoginRequiredMixin, TemplateView):
    """Manage notification preferences."""
    template_name = 'academics/notification_settings.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = self.request.user.student
            prefs, _ = NotificationPreference.objects.get_or_create(student=student)
            
            context['student'] = student
            context['preferences'] = prefs
            context['notification_types'] = NotificationPreference.NOTIFICATION_TYPES
        except ObjectDoesNotExist:
            context['error'] = 'Student profile not found.'
            context['student'] = None
        except Exception as e:
            context['error'] = f'Error loading preferences: {str(e)}'
            context['student'] = None
        
        return context
    
    def post(self, request):
        try:
            student = request.user.student
            prefs, _ = NotificationPreference.objects.get_or_create(student=student)
            
            # Update preferences
            prefs.enabled_notifications = request.POST.get('notifications', 'all')
            prefs.email_on_alerts = request.POST.get('email_alerts') == 'on'
            prefs.dashboard_alerts = request.POST.get('dashboard_alerts') == 'on'
            prefs.save()
            
            messages.success(request, 'Notification preferences updated successfully!')
            return render(request, self.template_name, {
                'student': student,
                'preferences': prefs,
                'notification_types': NotificationPreference.NOTIFICATION_TYPES
            })
        except Exception as e:
            messages.error(request, f'Error updating preferences: {str(e)}')
            return self.get(request)


class GradeAlertsListView(LoginRequiredMixin, ListView):
    """Display list of grade alerts."""
    template_name = 'academics/grade_alerts.html'
    context_object_name = 'alerts'
    paginate_by = 10
    login_url = 'accounts:login'
    
    def get_queryset(self):
        student = self.request.user.student
        return GradeAlert.objects.filter(student=student).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.request.user.student
        context['unread_count'] = GradeAlert.objects.filter(
            student=self.request.user.student,
            is_read=False
        ).count()
        return context


class MarkAlertAsReadView(LoginRequiredMixin, View):
    """Mark an alert as read (AJAX)."""
    login_url = 'accounts:login'
    
    def post(self, request, alert_id):
        try:
            student = request.user.student
            alert = GradeAlert.objects.get(id=alert_id, student=student)
            alert.is_read = True
            alert.save()
            return JsonResponse({'status': 'success', 'message': 'Alert marked as read'})
        except GradeAlert.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Alert not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class ProjectionPDFExportView(LoginRequiredMixin, View):
    """Export graduation plan as PDF."""
    login_url = 'accounts:login'
    
    def get(self, request):
        try:
            student = request.user.student
            gpa_data = GradeCalculator.calculate_wma(student)
            
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from io import BytesIO
            from django.utils import timezone
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*72, bottomMargin=0.5*72)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#4CAF50'),
                spaceAfter=12,
                alignment=1
            )
            elements.append(Paragraph("GRADUATION PLAN", title_style))
            elements.append(Spacer(1, 12))
            
            # Current Status
            status_info = [
                ['Student:', student.user.get_full_name()],
                ['Current GPA:', f"{gpa_data.get('gpa', 0):.2f}"],
                ['Honors Level:', gpa_data.get('honors_level', 'Pass')],
                ['Units Completed:', str(gpa_data.get('units_completed', 0))],
            ]
            status_table = Table(status_info, colWidths=[2*72, 4*72])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(status_table)
            elements.append(Spacer(1, 12))
            
            # Projections
            targets = {
                'First Class Honours': 70.0,
                'Second Class (Upper)': 60.0,
                'Second Class (Lower)': 50.0,
                'Pass': 40.0,
            }
            
            proj_data = [['Target', 'Required Average', 'Achievable']]
            for target_name, target_gpa in targets.items():
                projection = GradeCalculator.project_required_average(student, target_gpa)
                proj_data.append([
                    target_name,
                    f"{projection.get('required_average', 0):.2f}%" if projection.get('required_average') else 'N/A',
                    '✓ Yes' if projection.get('is_achievable') else '✗ No'
                ])
            
            proj_table = Table(proj_data, colWidths=[2*72, 2*72, 2*72])
            proj_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ]))
            elements.append(Paragraph("GRADUATION TARGETS", title_style))
            elements.append(Spacer(1, 8))
            elements.append(proj_table)
            
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Report Generated: " + str(timezone.now().strftime('%Y-%m-%d %H:%M:%S')), styles['Normal']))
            
            doc.build(elements)
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="graduation_plan_{student.registration_number}.pdf"'
            return response
        except ObjectDoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('academics:dashboard')
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('academics:projection')


