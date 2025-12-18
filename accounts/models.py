from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    """
    Extended student profile with JKUAT-specific fields.
    Extends Django's built-in User model.
    """
    YEAR_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="e.g., SCT211-0001/2021"
    )
    course = models.CharField(
        max_length=100, 
        help_text="e.g., Bachelor of Science in Computer Science"
    )
    year_of_study = models.IntegerField(
        choices=YEAR_CHOICES,
        default=1
    )
    academic_year = models.CharField(
        max_length=9,
        default="2024/2025",
        help_text="e.g., 2024/2025"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Students"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registration_number})"

