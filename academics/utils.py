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
                'honors_level': 'No data available'
            }
        
        # Calculate totals
        total_points = Decimal('0.00')
        total_credit_units = 0
        failed_count = 0
        
        for result in results:
            # Points = (Score * Credit Units) / 100
            points = Decimal(result.score) * Decimal(result.unit.credit_units) / Decimal('100')
            total_points += points
            total_credit_units += result.unit.credit_units
            
            if result.grade == 'E':  # Fail
                failed_count += 1
        
        # Calculate GPA/WMA
        if total_credit_units > 0:
            gpa = round(total_points / Decimal(total_credit_units), 2)
        else:
            gpa = Decimal('0.00')
        
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
        total_units_after = current_credits + remaining_units
        target_total_points = (target_gpa * total_units_after) / 100
        
        # Calculate required points from remaining units
        required_points = target_total_points - current_points
        
        # Calculate required average score
        if remaining_units > 0:
            required_average = (required_points / remaining_units) * 100
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
