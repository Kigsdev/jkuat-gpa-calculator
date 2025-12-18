from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Student


class LoginView(View):
    """Handle student login with registration number."""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('academics:dashboard')
        return render(request, self.template_name, {})
    
    def post(self, request):
        registration_number = request.POST.get('registration_number', '').strip()
        password = request.POST.get('password', '')
        error = None
        
        if not registration_number:
            error = 'Registration number is required.'
        elif not password:
            error = 'Password is required.'
        
        if error:
            return render(request, self.template_name, {'error': error})
        
        try:
            student = Student.objects.get(registration_number=registration_number)
            user = authenticate(
                request,
                username=student.user.username,
                password=password
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('academics:dashboard')
            else:
                error = 'Invalid registration number or password.'
        except Student.DoesNotExist:
            error = 'Student with this registration number not found.'
        except Exception as e:
            error = f'An error occurred: {str(e)}'
        
        return render(request, self.template_name, {'error': error})


class LogoutView(LoginRequiredMixin, View):
    """Handle student logout."""
    login_url = 'accounts:login'
    
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class RegisterView(View):
    """Handle student registration."""
    template_name = 'accounts/register.html'
    
    def get(self, request):
        return render(request, self.template_name, {})
    
    def post(self, request):
        return render(request, self.template_name, {})


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

