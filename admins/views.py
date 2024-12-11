from django.shortcuts import render, redirect
from django.views import View
from .permissions import OnlySuperUser
from organizations.models import UserProfile, Organizations
from django.db.models import Q
from organizations.models import EquipmentName, Organizations, Regions, RoomsEquipment
from .forms import CreateEquipmentNameForm
from django.http import JsonResponse

class Dashboard(View):
    def get(self, request):
        organization_count = Organizations.objects.count()
        user_count = UserProfile.objects.count()
        equipment_count = RoomsEquipment.objects.count()
        inclusive_organization_count = Organizations.objects.filter(is_inclusive=True).count()
        non_inclusive_organization_count = organization_count - inclusive_organization_count

        context = {
            'organization_count': organization_count,
            'user_count': user_count,
            'equipment_count': equipment_count,
            'inclusive_organization_count': inclusive_organization_count,
            'non_inclusive_organization_count': non_inclusive_organization_count,
        }
        return render(request, 'admins/dashboard.html', context)

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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.filter_organizations(request)

        orgs = Organizations.objects.all()
        context = {
            'orgs': orgs,
            'regions_list': Regions.objects.all(),
            'count_number_orgs': orgs.count()
        }
        return render(request, 'admins/org/org-list.html', context)

    def filter_organizations(self, request):
        region_id = request.GET.get("region_id")
        organization_type = request.GET.get("organization_type")
        is_inclusive = request.GET.get("is_inclusive")

        organizations = Organizations.objects.all()

        if region_id and region_id != "defaultRegion":
            organizations = organizations.filter(region_id=region_id)

        if organization_type and organization_type != "default":
            organizations = organizations.filter(education_type=organization_type)

        if is_inclusive and is_inclusive != "defaultInclusive":
            is_inclusive = is_inclusive == "ha"
            organizations = organizations.filter(is_inclusive=is_inclusive)

        data = [
            {
                "name": org.name,
                "education_type": org.get_education_type_display(),
                "students_amount": org.students_amount,
                "is_inclusive": "Ha" if org.is_inclusive else "Yo'q",
                "region": org.region.name,
                "admin": org.admin.fio
            }
            for org in organizations
        ]
        return JsonResponse({"organizations": data})
