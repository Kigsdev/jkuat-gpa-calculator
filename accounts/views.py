from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
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
        registration_number = request.POST.get('registration_number')
        password = request.POST.get('password')
        
        try:
            student = Student.objects.get(registration_number=registration_number)
            user = authenticate(
                request,
                username=student.user.username,
                password=password
            )
            if user is not None:
                login(request, user)
                return redirect('academics:dashboard')
            else:
                return render(request, self.template_name, 
                            {'error': 'Invalid registration number or password.'})
        except Student.DoesNotExist:
            return render(request, self.template_name,
                        {'error': 'Student with this registration number not found.'})


class LogoutView(LoginRequiredMixin, View):
    """Handle student logout."""
    login_url = 'accounts:login'
    
    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class RegisterView(View):
    """Handle student registration."""
    template_name = 'accounts/register.html'
    
    def get(self, request):
        return render(request, self.template_name, {})
    
    def post(self, request):
        # Registration logic to be implemented
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

