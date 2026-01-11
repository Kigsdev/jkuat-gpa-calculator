"""
Grading utility functions for GPA calculation.
Implements JKUAT-specific grading standards and calculations.
"""

from decimal import Decimal
from typing import Dict, Tuple, List
from .models import Result, Student, AcademicYear


class GradeCalculator:
    """
    Utility class for calculating grades and GPA based on JKUAT standards.
    """
    
    # Grade boundaries based on JKUAT standards
    GRADE_BOUNDARIES = {
        'A': (70, 100, 'First Class Honours'),
        'B': (60, 69, 'Second Class Honours (Upper Division)'),
        'C': (50, 59, 'Second Class Honours (Lower Division)'),
        'D': (40, 49, 'Pass'),
        'E': (0, 39, 'Fail'),
    }
    
    @staticmethod
    def get_grade(score: int) -> Tuple[str, str]:
        """
        Determine grade and honors level from score.
        
        Args:
            score: Score out of 100
            
        Returns:
            Tuple of (grade, honors_level)
        """
        for grade, (min_score, max_score, honors) in GradeCalculator.GRADE_BOUNDARIES.items():
            if min_score <= score <= max_score:
                return grade, honors
        return 'E', 'Fail'
    
    @staticmethod
    def calculate_wma(student: Student, academic_year: AcademicYear = None) -> Dict:
        """
        Calculate Weighted Mean Average (WMA) for a student.
        
        Args:
            student: Student instance
            academic_year: Optional AcademicYear filter
            
        Returns:
            Dictionary with GPA information:
            {
                'gpa': float,
                'total_points': float,
                'total_credit_units': int,
                'units_completed': int,
                'failed_units': int,
                'honors_level': str
            }
        """
        try:
            # Get results for the student
            if academic_year:
                results = Result.objects.filter(
                    student=student,
                    unit__academic_year=academic_year
                ).select_related('unit')
            else:
                results = Result.objects.filter(student=student).select_related('unit')
            
            if not results.exists():
                return {
                    'gpa': 0.00,
                    'total_points': 0.00,
                    'total_credit_units': 0,
                    'units_completed': 0,
                    'failed_units': 0,
                    'honors_level': 'No grades recorded yet'
                }
            
            # Calculate totals with validation
            total_points = Decimal('0.00')
            total_credit_units = 0
            failed_count = 0
            
            for result in results:
                # Validate score is in range
                if result.score is None or result.score < 0 or result.score > 100:
                    continue
                    
                # Points = Score * Credit Units
                points = Decimal(str(result.score)) * Decimal(result.unit.credit_units)
                total_points += points
                total_credit_units += result.unit.credit_units
                
                if result.grade == 'E':  # Fail
                    failed_count += 1
            
            # Calculate GPA/WMA: Total weighted points / Total credit units
            if total_credit_units > 0:
                gpa = float(round(total_points / Decimal(total_credit_units), 2))
            else:
                gpa = 0.00
            
            # Determine overall honors level
            if gpa >= 70:
                honors = 'First Class Honours'
            elif gpa >= 60:
                honors = 'Second Class Honours (Upper Division)'
            elif gpa >= 50:
                honors = 'Second Class Honours (Lower Division)'
            elif gpa >= 40:
                honors = 'Pass'
            else:
                honors = 'Fail'
            
            return {
                'gpa': gpa,
                'total_points': float(total_points),
                'total_credit_units': total_credit_units,
                'units_completed': results.exclude(grade='E').count(),
                'failed_units': failed_count,
                'honors_level': honors
            }
        except Exception as e:
            print(f"Error calculating WMA for {student}: {str(e)}")
            return {
                'gpa': 0.00,
                'total_points': 0.00,
                'total_credit_units': 0,
                'units_completed': 0,
                'failed_units': 0,
                'honors_level': f'Error: {str(e)[:50]}'
            }
        
        # Determine overall honors level
        gpa_float = float(gpa)
        if gpa_float >= 70:
            honors_level = 'First Class Honours'
        elif gpa_float >= 60:
            honors_level = 'Second Class Honours (Upper Division)'
        elif gpa_float >= 50:
            honors_level = 'Second Class Honours (Lower Division)'
        elif gpa_float >= 40:
            honors_level = 'Pass'
        else:
            honors_level = 'Below Pass'
        
        return {
            'gpa': float(gpa),
            'total_points': float(total_points),
            'total_credit_units': total_credit_units,
            'units_completed': results.count(),
            'failed_units': failed_count,
            'honors_level': honors_level
        }
    
    @staticmethod
    def project_required_average(
        student: Student,
        target_gpa: float,
        remaining_units: int,
        academic_year: AcademicYear = None
    ) -> Dict:
        """
        Calculate the required average in remaining units to achieve target GPA.
        
        Args:
            student: Student instance
            target_gpa: Target GPA (e.g., 70 for First Class)
            remaining_units: Number of remaining units
            academic_year: Optional AcademicYear filter
            
        Returns:
            Dictionary with projection information:
            {
                'required_average': float,
                'target_gpa': float,
                'current_gpa': float,
                'is_achievable': bool,
                'message': str
            }
        """
        # Get current GPA
        current_data = GradeCalculator.calculate_wma(student, academic_year)
        current_gpa = current_data['gpa']
        current_points = current_data['total_points']
        current_credits = current_data['total_credit_units']
        
        if remaining_units <= 0:
            return {
                'required_average': None,
                'target_gpa': target_gpa,
                'current_gpa': current_gpa,
                'is_achievable': current_gpa >= target_gpa,
                'message': 'No remaining units to complete.'
            }
        
        # Calculate required total points
        total_units_after = current_credits + (remaining_units * 3)  # Assuming avg credit units is 3
        target_total_points = target_gpa * total_units_after
        
        # Calculate required points from remaining units
        required_points = target_total_points - current_points
        
        # Calculate required average score (assuming each remaining unit has 3 credit units)
        remaining_credit_units = remaining_units * 3
        if remaining_credit_units > 0:
            required_average = required_points / remaining_credit_units
        else:
            required_average = 0
        
        # Cap at 100 (maximum possible)
        required_average = min(100, max(0, float(required_average)))
        
        # Check achievability
        is_achievable = required_average <= 100
        
        if required_average > 100:
            message = f"Target GPA of {target_gpa}% is NOT achievable even with 100% in remaining units."
        elif required_average >= 90:
            message = f"Excellent performance needed: average {required_average:.1f}% in {remaining_units} remaining units."
        elif required_average >= 75:
            message = f"Good performance needed: average {required_average:.1f}% in {remaining_units} remaining units."
        else:
            message = f"Average {required_average:.1f}% needed in {remaining_units} remaining units."
        
        return {
            'required_average': float(required_average),
            'target_gpa': target_gpa,
            'current_gpa': current_gpa,
            'is_achievable': is_achievable,
            'message': message
        }
    
    @staticmethod
    def get_grade_distribution(student: Student) -> Dict[str, int]:
        """
        Get count of each grade for a student across all units.
        
        Args:
            student: Student instance
            
        Returns:
            Dictionary with grade counts: {'A': 5, 'B': 3, ...}
        """
        results = Result.objects.filter(student=student)
        distribution = {grade: 0 for grade in ['A', 'B', 'C', 'D', 'E']}
        
        for result in results:
            distribution[result.grade] += 1
        
        return distribution
    
    @staticmethod
    def get_transcript(student: Student, academic_year: AcademicYear = None) -> List[Dict]:
        """
        Get detailed transcript for a student.
        
        Args:
            student: Student instance
            academic_year: Optional AcademicYear filter
            
        Returns:
            List of dictionaries with unit details and grades
        """
        if academic_year:
            results = Result.objects.filter(
                student=student,
                unit__academic_year=academic_year
            ).select_related('unit').order_by('unit__code')
        else:
            results = Result.objects.filter(student=student).select_related('unit').order_by('unit__code')
        
        transcript = []
        for result in results:
            transcript.append({
                'code': result.unit.code,
                'name': result.unit.name,
                'credit_units': result.unit.credit_units,
                'score': result.score,
                'grade': result.grade,
                'points': float(result.points),
                'honors_level': GradeCalculator.get_grade(result.score)[1]
            })
        
        return transcript


class PDFGenerator:
    """
    Utility class for generating PDF transcripts and documents.
    Uses reportlab for PDF generation.
    """
    
    @staticmethod
    def generate_transcript_pdf(student: Student, gpa_data: Dict) -> bytes:
        """
        Generate academic transcript as PDF.
        
        Args:
            student: Student instance
            gpa_data: GPA calculation data from GradeCalculator
            
        Returns:
            PDF bytes for download
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from io import BytesIO
        
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
            alignment=1  # Center
        )
        elements.append(Paragraph("ACADEMIC TRANSCRIPT", title_style))
        elements.append(Paragraph("JKUAT GPA Calculator", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Student Info Section
        student_info = [
            ['Registration Number:', student.registration_number],
            ['Name:', student.user.get_full_name()],
            ['Email:', student.user.email],
            ['Course:', student.course],
            ['Year of Study:', str(student.year_of_study)],
        ]
        student_table = Table(student_info, colWidths=[2*72, 4*72])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 12))
        
        # GPA Summary Section
        gpa_summary = [
            ['GPA', 'Honors Level', 'Units Completed', 'Total Points'],
            [
                f"{gpa_data.get('gpa', 0):.2f}",
                gpa_data.get('honors_level', 'Pass'),
                str(gpa_data.get('units_completed', 0)),
                f"{gpa_data.get('total_points', 0):.1f}"
            ]
        ]
        gpa_table = Table(gpa_summary, colWidths=[1.5*72, 2*72, 1.5*72, 1.5*72])
        gpa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(gpa_table)
        elements.append(Spacer(1, 20))
        
        # Courses/Units Section
        transcript = GradeCalculator.get_transcript(student)
        if transcript:
            elements.append(Paragraph("COURSE DETAILS", title_style))
            elements.append(Spacer(1, 8))
            
            course_data = [['Code', 'Unit Name', 'Credits', 'Score', 'Grade', 'Points']]
            for item in transcript:
                course_data.append([
                    item['code'],
                    item['name'][:30],
                    str(item['credit_units']),
                    f"{item['score']}%",
                    item['grade'],
                    f"{item['points']:.1f}"
                ])
            
            course_table = Table(course_data, colWidths=[0.8*72, 2.2*72, 0.7*72, 0.7*72, 0.6*72, 0.8*72])
            course_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
            ]))
            elements.append(course_table)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Report Generated: " + str(timezone.now().strftime('%Y-%m-%d %H:%M:%S')), styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


class AnalyticsCalculator:
    """
    Utility class for calculating grade analytics and trends for Phase 5.
    """
    
    @staticmethod
    def calculate_analytics(student: Student) -> Dict:
        """
        Calculate comprehensive grade analytics for a student.
        
        Args:
            student: Student instance
            
        Returns:
            Dictionary with analytics data
        """
        from django.db.models import Avg, Q
        
        results = Result.objects.filter(student=student).select_related('unit')
        
        if not results.exists():
            return {
                'average_score': 0,
                'best_unit': None,
                'worst_unit': None,
                'struggling_units': [],
                'units_at_risk': 0,
                'gpa_trend': 'stable'
            }
        
        # Average grade score
        avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
        
        # Best and worst units
        best_result = results.order_by('-score').first()
        worst_result = results.order_by('score').first()
        
        # Struggling units (grades below C - score < 50)
        struggling = results.filter(score__lt=50)
        struggling_list = [{'code': r.unit.code, 'name': r.unit.name, 'score': r.score} for r in struggling]
        
        # Units at risk (score < 60)
        units_at_risk = results.filter(score__lt=60).count()
        
        # Trend calculation (comparing recent vs earlier grades)
        all_results = list(results.order_by('created_at'))
        if len(all_results) > 2:
            recent_avg = sum([r.score for r in all_results[-3:]]) / min(3, len(all_results[-3:]))
            earlier_avg = sum([r.score for r in all_results[:3]]) / min(3, len(all_results[:3]))
            
            if recent_avg > earlier_avg + 5:
                trend = 'improving'
            elif recent_avg < earlier_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'average_score': round(avg_score, 2),
            'best_unit': f"{best_result.unit.code} ({best_result.score}%)" if best_result else None,
            'worst_unit': f"{worst_result.unit.code} ({worst_result.score}%)" if worst_result else None,
            'struggling_units': struggling_list,
            'units_at_risk': units_at_risk,
            'gpa_trend': trend,
            'total_units': results.count()
        }
    
    @staticmethod
    def check_grade_alerts(student: Student, gpa_data: Dict) -> List[Dict]:
        """
        Check for alert conditions and generate alerts.
        
        Args:
            student: Student instance
            gpa_data: GPA calculation data
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Check for low grades
        low_grades = Result.objects.filter(student=student, score__lt=50).count()
        if low_grades > 0:
            alerts.append({
                'type': 'low_grade',
                'title': 'Low Grades Alert',
                'message': f'You have {low_grades} unit(s) with grades below 50%. Consider reviewing these units.'
            })
        
        # Check for honor level thresholds
        current_gpa = gpa_data.get('gpa', 0)
        if 68 <= current_gpa < 70:
            alerts.append({
                'type': 'honor_approaching',
                'title': 'First Class Honours Within Reach',
                'message': f'You are {70 - current_gpa:.2f} points away from First Class Honours!'
            })
        elif 58 <= current_gpa < 60:
            alerts.append({
                'type': 'honor_approaching',
                'title': 'Second Class (Upper) Within Reach',
                'message': f'You are {60 - current_gpa:.2f} points away from Second Class (Upper) Division!'
            })
        
        return alerts


from django.utils import timezone
