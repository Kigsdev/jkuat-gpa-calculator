from django import forms
from django.contrib.auth.models import User
from .models import Student


class LoginForm(forms.Form):
    """Form for student login using registration number."""
    registration_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., SCT211-0001/2021',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        reg_num = cleaned_data.get('registration_number', '').strip()
        password = cleaned_data.get('password')
        
        if not reg_num:
            self.add_error('registration_number', 'Registration number is required.')
        
        if not password:
            self.add_error('password', 'Password is required.')
        
        return cleaned_data


class RegisterForm(forms.ModelForm):
    """Form for student registration with validation."""
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
        }
    
    def clean(self):
        """Validate password match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile."""
    class Meta:
        model = Student
        fields = ['registration_number', 'course', 'year_of_study', 'academic_year']
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'placeholder': 'Registration Number (Read-only)'
            }),
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Science in Computer Science'
            }),
            'year_of_study': forms.Select(attrs={
                'class': 'form-control'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024/2025'
            }),
        }
    
    def clean_academic_year(self):
        """Validate academic year format."""
        academic_year = self.cleaned_data.get('academic_year')
        if academic_year and '/' not in academic_year:
            raise forms.ValidationError('Academic year must be in format: YYYY/YYYY (e.g., 2024/2025)')
        return academic_year
    
    def clean_course(self):
        """Validate course name."""
        course = self.cleaned_data.get('course')
        if course and len(course) < 3:
            raise forms.ValidationError('Course name must be at least 3 characters long.')
        return course
