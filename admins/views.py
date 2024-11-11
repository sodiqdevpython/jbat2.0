from django.shortcuts import render, redirect
from django.views import View
from .permissions import OnlySuperUser
from organizations.models import UserProfile
from django.db.models import Q
from organizations.models import EquipmentName, Organizations
from .forms import CreateEquipmentNameForm

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

class EquipmentList(View):
    def get(self, request):
        form = CreateEquipmentNameForm()
        rooms_equipments = EquipmentName.objects.only('name')
        context = {
            'data': rooms_equipments,
            'count_number': rooms_equipments.count(),
            'form': form
        }
        return render(request, 'admins/org/equipments-list.html', context)
    
    def post(self, request):
        form = CreateEquipmentNameForm(request.POST or None)
        if form.is_valid():
            form.save()
        return redirect('admin_equipment_list')
        

class MaterialTechnicBase(View, OnlySuperUser):
    def get(self, request):
        orgs = Organizations.objects.only('id','name')
        context = {
            'orgs': orgs
        }
        return render(request, 'admins/org/material-technic-base.html', context)
    
class OrganizationList(View, OnlySuperUser):
    def get(self, request):
        orgs = Organizations.objects.all()
        context = {
            'orgs': orgs
        }
        return render(request, 'admins/org/org-list.html', context)