from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, ContactForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FAQ


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('admin_dashboard')
        else:
            return render(request, 'org/auth/login.html')
    
    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            get_data = form.cleaned_data
            user = authenticate(request, username=get_data['username'], password=get_data['password'])
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                error_message = "ID raqam yoki parol xato !"

                context = {
                    'form': form,
                    'error_message': error_message
                }

                return render(request, 'org/auth/login.html', context)


class LogoutView(View, LoginRequiredMixin):
    def get(self, request):
        logout(request)
        return redirect('public')


class PublicView(View):
    def get(self, request):
        faqs = FAQ.objects.all()[:10]
        context = {
            'faq': faqs
        }
        return render(request, 'index.html', context)
    
    def post(self, request):
        form = ContactForm(request.POST or None)
        if form.is_valid():
            form.save()
        
        return redirect('public')