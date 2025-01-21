from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from datetime import date, timedelta
from organizations.models import Organizations, RoomsEquipment, Message
from django.core.paginator import Paginator
from organizations.forms import MessageForm
from django.db.models import Count

class UserDashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'

    def get(self, request):
        user = request.user
        try:
            organization = Organizations.objects.get(admin__user=user)
        except Organizations.DoesNotExist:
            context = {'no_organization': True}
            return render(request, self.template_name, context)

        eq_type_counts = RoomsEquipment.objects.filter(organization_for=organization)\
        .values('equipment_type')\
        .annotate(total=Count('equipment_type'))
        org_name = organization.name
        org_student_count = organization.students_amount or 0
        org_ball = organization.ball or 0
        org_inclusive = "Ha" if organization.is_inclusive else "Yo'q"
        org_power = organization.power or 0
        org_region = organization.region.name if organization.region else "Noma'lum"

        # Shahar/Tuman
        if organization.city:
            org_city_district = "Shahar: " + organization.city.name
        elif organization.district:
            org_city_district = "Tuman: " + organization.district.name
        else:
            org_city_district = "Shahar/Tuman belgilanmagan"

        # RoomsEquipment — umumiy son
        equipments = RoomsEquipment.objects.filter(organization_for=organization)
        total_equipments = equipments.count()

        # So‘nggi 3 oy uchun jihoz statistika (entry date bo‘yicha)
        equipment_data = self.get_equipment_data_3months(equipments)

        context = {
            'org_name': org_name,
            'org_student_count': org_student_count,
            'org_ball': org_ball,
            'org_inclusive': org_inclusive,
            'org_power': org_power,
            'org_region': org_region,
            'org_city_district': org_city_district,
            'total_equipments': total_equipments,
            'equipment_data': equipment_data,
            'organization': organization,
        }
        return render(request, self.template_name, context)

    def get_equipment_data_3months(self, equipments):
        """
        Oxirgi 3 oy bo'yicha jihoz kiritilgan sanani tahlil qilib,
        [oy1, oy2, oy3] shaklda son qaytaradi.
        """
        today = date.today()
        current_month = today.month
        current_year = today.year

        result = [0, 0, 0]  # 3 ta oy
        for eq in equipments:
            if eq.entered_date:
                eq_month = eq.entered_date.month
                eq_year = eq.entered_date.year
                month_diff = (current_year - eq_year) * 12 + (current_month - eq_month)
                if 0 <= month_diff <= 2:
                    index = 2 - month_diff
                    result[index] += 1
        return result


class OrganizationDetailView(LoginRequiredMixin, View):
    template_name = "users/org-detail.html"

    def get(self, request, pk):
        organization = get_object_or_404(Organizations, id=pk)
        admin_profile = organization.admin
        equipments = RoomsEquipment.objects.filter(organization_for=organization)

        context = {
            'organization': organization,
            'admin_profile': admin_profile,
            'equipments': equipments,
        }
        return render(request, self.template_name, context)


def read(request):
    return render(request, 'users/read.html')

def add(request):
    return render(request, 'users/add.html')


class InboxView(LoginRequiredMixin, View):
    def get(self, request):
        messages_list = Message.objects.filter(recipient=request.user).order_by('-timestamp')
        paginator = Paginator(messages_list, 10)
        page_number = request.GET.get('page')
        messages = paginator.get_page(page_number)
        context = {
            'messages': messages
        }
        return render(request, 'users/inbox.html', context)


class SentView(LoginRequiredMixin, View):
    def get(self, request):
        messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
        context = {
            'messages': messages
        }
        return render(request, 'users/sent.html', context)


class MessageDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        if message.recipient != request.user and message.sender != request.user:
            return redirect('inbox')
        if message.recipient == request.user and not message.is_read:
            message.is_read = True
            message.save()
        context = {
            'message': message
        }
        return render(request, 'users/message_detail.html', context)

class UserOrganizationDetailView(LoginRequiredMixin, View):
    template_name = "users/org-detail.html"

    def get(self, request, pk):
        organization = get_object_or_404(Organizations, id=pk)

        user_profile = getattr(request.user, 'user_profile', None)
        if not user_profile:
            return redirect('user_dashboard')

        my_org = Organizations.objects.filter(admin=user_profile).first()
        if my_org != organization and not request.user.is_superuser:
            return redirect('user_dashboard')

        admin_profile = organization.admin

        eqs = RoomsEquipment.objects.filter(organization_for=organization).order_by('-created')

        student_count = organization.students_amount or 0
        total_equipment = eqs.count()
        paginator = Paginator(eqs, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        months_count = 3
        today = date.today()
        months = [
            (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            for i in range(months_count)
        ]
        months = sorted(months)
        monthly_equipment_data = []
        for m in months:
            c = eqs.filter(entered_date__year=m.year, entered_date__month=m.month).count()
            monthly_equipment_data.append(c)
        months_list = [m.strftime("%b %Y") for m in months]

        equipment_history = []
        for eq in eqs:
            eq_hist = eq.history.all().order_by('-history_date')
            equipment_history.extend(eq_hist)
        equipment_history.sort(key=lambda h: h.history_date, reverse=True)

        context = {
            'organization': organization,
            'admin_profile': admin_profile,

            'student_count': student_count,
            'total_equipment': total_equipment,

            'page_obj': page_obj,

            'months_list': months_list,
            'monthly_equipment_data': monthly_equipment_data,
            'equipment_history': equipment_history,
        }
        return render(request, self.template_name, context)

class ComposeMessageView(LoginRequiredMixin, View):
    def get(self, request):
        form = MessageForm(current_user=request.user)
        return render(request, 'users/compose.html', {'form': form})
    
    def post(self, request):
        form = MessageForm(request.POST, current_user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('sent2')
        return render(request, 'users/compose.html', {'form': form})

from users.forms import EquipmentCreateUpdateForm
from organizations.models import RoomsEquipment, Organizations

class EquipmentCreateView(LoginRequiredMixin, View):
    template_name = 'users/equipment_create.html'

    def get(self, request):
        form = EquipmentCreateUpdateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EquipmentCreateUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            user_profile = getattr(request.user, 'user_profile', None)
            equipment.author = user_profile
            org = Organizations.objects.filter(admin=user_profile).first()
            equipment.organization_for = org
            equipment.save()
            return redirect('user_dashboard')
        return render(request, self.template_name, {'form': form})


class EquipmentUpdateView(LoginRequiredMixin, View):
    template_name = 'users/equipment_update.html'

    def get(self, request, pk):
        equipment = get_object_or_404(RoomsEquipment, pk=pk)
        user_profile = getattr(request.user, 'user_profile', None)
        if not user_profile:
            return redirect('user_dashboard')
        if equipment.organization_for and equipment.organization_for.admin != user_profile:
            return redirect('user_dashboard')

        form = EquipmentCreateUpdateForm(instance=equipment)
        return render(request, self.template_name, {
            'form': form,
            'equipment': equipment
        })

    def post(self, request, pk):
        equipment = get_object_or_404(RoomsEquipment, pk=pk)
        user_profile = getattr(request.user, 'user_profile', None)
        if not user_profile:
            return redirect('user_dashboard')
        if equipment.organization_for and equipment.organization_for.admin != user_profile:
            return redirect('user_dashboard')

        form = EquipmentCreateUpdateForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            eq = form.save(commit=False)
            eq.save()
            return redirect('user_dashboard')
        return render(request, self.template_name, {
            'form': form,
            'equipment': equipment
        })
    
class UserEquipmentListView(LoginRequiredMixin, View):
    template_name = 'users/equipment_list.html'

    def get(self, request):
        user_profile = getattr(request.user, 'user_profile', None)
        if not user_profile:
            return redirect('user_dashboard')

        organization = Organizations.objects.filter(admin=user_profile).first()
        if not organization:
            return render(request, self.template_name, {
                'no_organization': True
            })

        equipments = RoomsEquipment.objects.filter(organization_for=organization).order_by('-created')

        context = {
            'organization': organization,
            'equipments': equipments,
        }
        return render(request, self.template_name, context)
    
class EquipmentDetailView(LoginRequiredMixin, View):
    template_name = "users/equipment_detail.html"

    def get(self, request, pk):
        equipment = get_object_or_404(RoomsEquipment, pk=pk)

        context = {
            'equipment': equipment
        }
        return render(request, self.template_name, context)