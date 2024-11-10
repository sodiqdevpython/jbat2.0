from django.shortcuts import render
from django.views import View
from .permissions import OnlySuperUser
from organizations.models import UserProfile
from django.db.models import Q

class Dashboard(View):
    def get(self, request):
        return render(request, 'admins/dashboard.html')

class Users(View, OnlySuperUser):
    def get(self, request):
        profiles = UserProfile.objects.filter(is_active=True)
        context = {
            'profiles': profiles,
            'count_result': profiles.count
        }
        return render(request, 'admins/users/read.html', context)

class WorkerGroup(View):
    def get(self, request):
        return render(request, 'admins/users/worker-group.html')
    
class SearchUsers(View, OnlySuperUser):
    def get(self, request):
        input_data = request.GET.get('searched')
        searched = UserProfile.objects.filter(
            Q(first_name__icontains=input_data) | Q(last_name__icontains=input_data) | Q(tel_number__icontains=input_data)
        ) 
        context = {
            'searched': searched,
            'input_data': input_data
        }
        return render(request, 'admins/users/search.html', context)
    
class PageIsNotReady(View):
    def get(self, request):
        return render(request, 'admins/page-not-ready.html')