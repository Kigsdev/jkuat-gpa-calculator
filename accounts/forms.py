from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.validators import MinLengthValidator, RegexValidator
from .models import Student


class LoginForm(forms.Form):
    """Form for student login using registration number."""
    registration_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g., SCT211-0001/2021',
            'autofocus': True,
            'autocomplete': 'username'
        }),
        help_text='Your student registration number'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Remember me for 30 days'
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


class RegisterForm(UserCreationForm):
    """Form for student registration with validation and email verification."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        }),
        help_text='Required. We\'ll send a verification email.'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'First Name',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Last Name',
                'autocomplete': 'family-name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Username (4-30 characters)',
                'autocomplete': 'username'
            }),
        }
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password (min 8 characters)',
            'autocomplete': 'new-password'
        }),
        help_text='At least 8 characters. Mix of letters, numbers, and symbols recommended.'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email
    
    def clean_username(self):
        """Validate username."""
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise forms.ValidationError('Username must be at least 4 characters.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        user.is_active = False  # Require email verification
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    """Form for password reset requests."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        }),
        help_text='Enter the email associated with your account.'
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Form for setting new password during reset."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'New Password',
            'autocomplete': 'new-password'
        })
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm New Password',
            'autocomplete': 'new-password'
        })
    )


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
