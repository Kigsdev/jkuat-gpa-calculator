from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import Student


class AcademicYear(models.Model):
    """
    Represents an academic year/semester session.
    Example: Year 2, Semester 1 (2024/2025)
    """
    year = models.IntegerField(help_text="e.g., 2024")
    semester = models.IntegerField(
        choices=[(1, 'Semester 1'), (2, 'Semester 2')],
        default=1
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-semester']
        unique_together = ['year', 'semester']
        verbose_name_plural = "Academic Years"
    
    def __str__(self):
        return f"{self.year}/{self.year+1} - Semester {self.semester}"


class Unit(models.Model):
    """
    Represents a course unit/module.
    Stores unit code, name, and credit factors.
    """
    code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="e.g., MIT201"
    )
    name = models.CharField(max_length=200, help_text="e.g., Data Structures")
    credit_units = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Credit factor for the unit (typically 1-4)"
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE,
        related_name='units'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        unique_together = ['code', 'academic_year']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Result(models.Model):
    """
    Stores a student's score for a specific unit.
    Links Student ↔ Unit ↔ Score.
    """
    GRADE_CHOICES = [
        ('A', 'A (70-100%) - Excellent'),
        ('B', 'B (60-69%) - Good'),
        ('C', 'C (50-59%) - Satisfactory'),
        ('D', 'D (40-49%) - Pass'),
        ('E', 'E (0-39%) - Fail'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score out of 100"
    )
    grade = models.CharField(
        max_length=1, 
        choices=GRADE_CHOICES,
        blank=True,
        editable=False,
        help_text="Auto-calculated based on score"
    )
    points = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        blank=True,
        editable=False,
        help_text="Weighted points (score × credit_units)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['student', 'unit']
        verbose_name_plural = "Results"
    
    def __str__(self):
        return f"{self.student} - {self.unit.code}: {self.score}%"
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate grade and points."""
        # Auto-calculate grade based on score
        if self.score is not None:
            if self.score >= 70:
                self.grade = 'A'
            elif self.score >= 60:
                self.grade = 'B'
            elif self.score >= 50:
                self.grade = 'C'
            elif self.score >= 40:
                self.grade = 'D'
            else:
                self.grade = 'E'
            
            # Calculate weighted points (score * credit_units)
            self.points = self.score * self.unit.credit_units
        else:
            self.grade = None
            self.points = 0
        
        super().save(*args, **kwargs)
class GPACalculation(models.Model):
    """
    Stores calculated GPA/WMA for a student in a specific academic year.
    Useful for caching and historical tracking.
    """
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='gpa_calculations'
    )
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE,
        related_name='gpa_calculations'
    )
    gpa = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Weighted Mean Average (WMA)"
    )
    total_points = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Total weighted points"
    )
    total_credit_units = models.IntegerField(
        help_text="Total credit units completed"
    )
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year__year', '-academic_year__semester']
        unique_together = ['student', 'academic_year']
        verbose_name_plural = "GPA Calculations"
    
    def __str__(self):
        return f"{self.student} - {self.academic_year}: {self.gpa}"


class NotificationPreference(models.Model):
    """
    Stores student notification preferences for Phase 5 alerts.
    """
    NOTIFICATION_TYPES = [
        ('gpa_change', 'GPA Changes'),
        ('honor_threshold', 'Honor Level Threshold (within 2 points)'),
        ('low_grade', 'Grades Below Target'),
        ('all', 'All Notifications'),
    ]
    
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    enabled_notifications = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='all'
    )
    email_on_alerts = models.BooleanField(default=True)
    dashboard_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Notifications"


class GradeAlert(models.Model):
    """
    Stores alerts/notifications for students about GPA changes, thresholds, etc.
    """
    ALERT_TYPES = [
        ('gpa_increase', 'GPA Increased'),
        ('gpa_decrease', 'GPA Decreased'),
        ('honor_approaching', 'Approaching Honor Level'),
        ('low_grade', 'Low Grade Alert'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grade_alerts'
    )
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.alert_type}"


class GradeAnalytics(models.Model):
    """
    Stores grade analysis and trends for Phase 5 insights.
    """
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='grade_analytics'
    )
    average_grade_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Average score across all units"
    )
    best_performing_unit = models.CharField(max_length=50, blank=True)
    worst_performing_unit = models.CharField(max_length=50, blank=True)
    struggling_units = models.TextField(blank=True, help_text="JSON array of struggling units")
    gpa_trend = models.CharField(max_length=20, blank=True, help_text="'improving', 'stable', 'declining'")
    units_at_risk = models.IntegerField(default=0, help_text="Number of units with grades below C")
    last_calculated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Analytics"


