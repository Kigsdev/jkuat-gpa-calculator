from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .models import Student
from .forms import LoginForm, RegisterForm, StudentProfileForm


class LoginView(View):
    """Handle student login with registration number."""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('academics:dashboard')
        return render(request, self.template_name, {'form': LoginForm()})
    
    def post(self, request):
        form = LoginForm(request.POST)
        
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'error': 'Invalid form submission.'})
        
        registration_number = form.cleaned_data.get('registration_number')
        password = form.cleaned_data.get('password')
        
        try:
            student = Student.objects.get(registration_number=registration_number)
            user = authenticate(
                request,
                username=student.user.username,
                password=password
            )
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account has been disabled. Please contact the administrator.')
                    return render(request, self.template_name, {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or "Student"}!')
                
                # Redirect to next page if provided
                next_page = request.GET.get('next', 'academics:dashboard')
                return redirect(next_page)
            else:
                form.add_error(None, 'Invalid registration number or password.')
        except Student.DoesNotExist:
            form.add_error('registration_number', 'Student with this registration number not found.')
        except Exception as e:
            form.add_error(None, f'An error occurred. Please try again later.')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    """Handle student logout."""
    login_url = 'accounts:login'
    
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class RegisterView(FormView):
    """Handle student registration with email verification."""
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('academics:dashboard')
        return super().get(request)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Require email verification
        user.save()
        
        # Send verification email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_url = self.request.build_absolute_uri(
            reverse_lazy('accounts:verify-email', kwargs={'uidb64': uid, 'token': token})
        )
        
        try:
            send_mail(
                'Verify your JKUAT GPA Calculator account',
                f'Click the link below to verify your email:\n\n{verification_url}\n\nThis link expires in 24 hours.',
                'noreply@jkuat-gpa-calculator.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Check your email to verify your account.')
        except Exception as e:
            user.delete()
            messages.error(request, f'Error sending verification email. Please try again.')
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})


class VerifyEmailView(View):
    """Verify user email via token link."""
    
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Verification link is invalid or has expired.')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Verification link is invalid.')
        
        return redirect('accounts:login')


class CustomPasswordResetView(PasswordResetView):
    """Handle password reset requests."""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password-reset-done')
    
    def form_valid(self, form):
        messages.info(self.request, 'If an account exists with that email, you will receive password reset instructions.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Handle password reset confirmation."""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password-reset-complete')


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Handle password changes for authenticated users."""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password-change-done')
    login_url = 'accounts:login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)


class StudentProfileView(LoginRequiredMixin, TemplateView):
    """Display student profile information."""
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['student'] = self.request.user.student
        except Student.DoesNotExist:
            context['student'] = None
        return context

