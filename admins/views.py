from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count
from django.core.paginator import Paginator
from .permissions import OnlySuperUser
from organizations.models import UserProfile, Organizations
from django.db.models import Q
from organizations.models import EquipmentName, Organizations, Regions, RoomsEquipment
from .forms import CreateEquipmentNameForm, UserProfileUpdateForm, OrganizationUpdateForm
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta, date

class OrganizationEquipmentsView(View):
    def get(self, request, org_id):
        organization = get_object_or_404(Organizations, id=org_id)
        equipments = RoomsEquipment.objects.filter(organization_for=organization).order_by('-created')
        context = {
            'organization': organization,
            'equipments': equipments,  # BARCHA jihozlar
        }
        return render(request, 'admins/organization_equipment_list.html', context)
    
class OrganizationDetailView(View):
    def get(self, request, id):
        organization = get_object_or_404(Organizations, id=id)


        student_count = organization.students_amount or 0

        eqs = RoomsEquipment.objects.filter(organization_for=organization).order_by('-created')

        total_equipment = eqs.count()

        paginator = Paginator(eqs, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        months_count = 3
        today = date.today()
        months = [
            (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            for i in range(months_count)
        ]
        months = sorted(months)
        monthly_equipment_data = []
        for m in months:
            count_this_month = eqs.filter(
                entered_date__year=m.year,
                entered_date__month=m.month
            ).count()
            monthly_equipment_data.append(count_this_month)
        months_list = [m.strftime("%b %Y") for m in months]
        equipment_history = []
        for eq in eqs:
            eq_hist = eq.history.all().order_by('-history_date')
            equipment_history.extend(eq_hist)
        equipment_history.sort(key=lambda h: h.history_date, reverse=True)

        context = {
            'organization': organization,
            'student_count': student_count,
            'total_equipment': total_equipment,

            'page_obj': page_obj,

            'months_list': months_list,  
            'monthly_equipment_data': monthly_equipment_data, 

            'equipment_history': equipment_history,
        }
        return render(request, 'admins/organization-detail.html', context)

class Dashboard(View):
    def get(self, request):
        organization_count = Organizations.objects.count()
        user_count = UserProfile.objects.count()
        equipment_count = RoomsEquipment.objects.count()
        inclusive_organization_count = Organizations.objects.filter(is_inclusive=True).count()
        non_inclusive_organization_count = organization_count - inclusive_organization_count

        from datetime import date, timedelta
        today = date.today()
        months = [today.replace(day=1) - timedelta(days=30 * i) for i in range(10)][::-1]
        equipment_monthly_stats = [
            RoomsEquipment.objects.filter(entered_date__year=month.year, entered_date__month=month.month).count()
            for month in months
        ]

        context = {
            'organization_count': organization_count,
            'user_count': user_count,
            'equipment_count': equipment_count,
            'inclusive_organization_count': inclusive_organization_count,
            'non_inclusive_organization_count': non_inclusive_organization_count,
            'equipment_monthly_stats': equipment_monthly_stats,
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
        """
        Ajax bo'lmasa – sahifani to'liq render qilamiz:
          1) 10 tadan pagination
          2) top 10 eng ko'p jihozlangan
        Ajax bo'lsa – filter_organizations() javob qaytaradi.
        """
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.filter_organizations(request)

        page = request.GET.get('page', 1)
        orgs = Organizations.objects.all().order_by('-created')
        paginator = Paginator(orgs, 10)
        page_obj = paginator.get_page(page)

        top_10_orgs = Organizations.objects.annotate(
            equipment_count=Count('roomsequipment')
        ).order_by('-equipment_count')[:10]

        context = {
            'page_obj': page_obj,
            'regions_list': Regions.objects.all(),
            'count_number_orgs': orgs.count(),
            'top_10_orgs': top_10_orgs,
        }
        return render(request, 'admins/org/org-list.html', context)

    def filter_organizations(self, request):
        region_id = request.GET.get("region_id")
        organization_type = request.GET.get("organization_type")
        is_inclusive = request.GET.get("is_inclusive")
        page = request.GET.get("page", 1)

        organizations = Organizations.objects.all().order_by('-created')

        if region_id and region_id != "defaultRegion":
            organizations = organizations.filter(region_id=region_id)

        if organization_type and organization_type != "default":
            organizations = organizations.filter(education_type=organization_type)

        if is_inclusive and is_inclusive != "defaultInclusive":
            is_inclusive_bool = True if is_inclusive == "ha" else False
            organizations = organizations.filter(is_inclusive=is_inclusive_bool)

        paginator = Paginator(organizations, 10)
        page_obj = paginator.get_page(page)

        data = []
        start_count = page_obj.start_index()
        for idx, org in enumerate(page_obj.object_list, start=start_count):
            data.append({
                "index": idx,
                "id": str(org.id),  # pk
                "name": org.name,
                "education_type": org.get_education_type_display(),
                "students_amount": f"{org.students_amount} o'quvchi",
                "is_inclusive": "Ha" if org.is_inclusive else "Yo'q",
                "region": org.region.name,
                "admin": org.admin.fio if org.admin else "—",
            })

        return JsonResponse({
            "organizations": data,
            "has_next": page_obj.has_next(),
            "current_page": page_obj.number,
            "total_count": paginator.count,
        })

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

class UserUpdateView(OnlySuperUser, View):
    def get(self, request, pk):
        user_profile = get_object_or_404(UserProfile, pk=pk)
        form = UserProfileUpdateForm(instance=user_profile)
        return render(request, 'admins/user-update.html', {
            'form': form,
            'user_profile': user_profile
        })

    def post(self, request, pk):
        user_profile = get_object_or_404(UserProfile, pk=pk)
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Foydalanuvchi ma'lumotlari muvaffaqiyatli saqlandi!")
            return redirect('user_detail', id=pk)
        else:
            messages.error(request, "Ma'lumotlarni to'g'ri kiriting!")
            return render(request, 'admins/user-update.html', {
                'form': form,
                'user_profile': user_profile
            })
        
class OrganizationUpdateView(View, OnlySuperUser):
    def get(self, request, pk):
        organization = get_object_or_404(Organizations, pk=pk)
        form = OrganizationUpdateForm(instance=organization)
        context = {
            'form': form,
            'organization': organization,
        }
        return render(request, 'admins/org/organization-update.html', context)

    def post(self, request, pk):
        organization = get_object_or_404(Organizations, pk=pk)
        form = OrganizationUpdateForm(request.POST, instance=organization)

        if form.is_valid():
            form.save()
            messages.success(request, "Muassasa ma'lumotlari muvaffaqiyatli yangilandi!")
            return redirect('org_detail', id=organization.id)
        else:
            messages.error(request, "Iltimos, formadagi xatolarni tuzating.")
        
        context = {
            'form': form,
            'organization': organization,
        }
        return render(request, 'admins/org/organization-update.html', context)