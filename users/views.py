from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
from organizations.models import Organizations, RoomsEquipment, BaseClasses, Message
from django.core.paginator import Paginator
from organizations.forms import MessageForm

class UserDashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'

    def get(self, request):
        user = request.user

        # 1) Foydalanuvchiga biriktirilgan tashkilotni topish
        try:
            organization = Organizations.objects.get(admin__user=user)
        except Organizations.DoesNotExist:
            context = {'no_organization': True}
            return render(request, self.template_name, context)

        # 2) Tashkilot ma'lumotlari
        # Avvaldan mavjud maydonlar:
        organization = Organizations.objects.filter(admin__user=user).first()
        org_name = organization.name
        org_rating = organization.rating or "Noma'lum"
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

        # Qo‘shimcha statistika: rooms_count, eng ko‘p jihozlangan room, boshqalar
        # Masalan, RoomsEquipment orqali:
        equipments = RoomsEquipment.objects.filter(organization_for=organization)
        total_equipments = equipments.count()  # Barcha jihozlar soni
        # Xonalar: if room is foreignKey in RoomsEquipment or if it is in BaseClasses
        # misol: eng ko'p jihozlangan xonani topish
        # (faqat misol, loyihangizdagi real bog‘lanishlarga qarang)
        most_equipped_room_name = "Noma'lum"
        if equipments.exists():
            # group by room, count
            # misol sifatida python-level counting
            room_count_map = {}
            for eq in equipments:
                if eq.room:
                    room_id = eq.room.id
                    room_count_map[room_id] = room_count_map.get(room_id, 0) + 1
            if room_count_map:
                # eng ko'p jihozga ega xona
                max_room_id = max(room_count_map, key=room_count_map.get)
                # eq.room.name => BaseClassCategory
                # eq.room.subtitle => BaseClassSubtitle
                # eq.room.organization => ...
                # misol:
                from .models import BaseClasses  # agar shunaqa bo'lsa
                max_room_obj = BaseClasses.objects.filter(id=max_room_id).first()
                if max_room_obj:
                    most_equipped_room_name = max_room_obj.name.name
                else:
                    most_equipped_room_name = "Xona nomi aniqlanmadi"

        # 3) Jihozlar statistikasi: so‘nggi 3 oy
        equipment_data = self.get_equipment_data_3months(equipments)


        context = {
            'org_name': org_name,
            'org_rating': org_rating,
            'org_student_count': org_student_count,
            'org_ball': org_ball,
            'org_inclusive': org_inclusive,
            'org_power': org_power,
            'org_region': org_region,
            'org_city_district': org_city_district,

            'total_equipments': total_equipments,
            'most_equipped_room': most_equipped_room_name,

            'equipment_data': equipment_data,
            'organization': organization
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

        result = [0, 0, 0]
        for eq in equipments:
            if eq.entered_date:
                eq_month = eq.entered_date.month
                eq_year = eq.entered_date.year
                # Oy farqi
                month_diff = (current_year - eq_year) * 12 + (current_month - eq_month)
                # 0 => joriy oy, 1 => oldingi oy, 2 => undan oldingi oy
                if 0 <= month_diff <= 2:
                    index = 2 - month_diff
                    result[index] += 1
        return result


class OrganizationDetailView(LoginRequiredMixin, View):
    template_name = "users/org-detail.html"

    def get(self, request, pk):
        # pk => UUID (BaseModel'dagi primary key)
        organization = get_object_or_404(Organizations, id=pk)

        # 1) Muassasa admin profili
        # Agar organization.admin = UserProfile bo'lsa, shu ob'ektni olamiz.
        admin_profile = organization.admin

        # 2) BaseClasses => shu muassasaga tegishli sinflar ro'yxati
        base_classes = BaseClasses.objects.filter(organization=organization)

        # 3) RoomsEquipment => shu muassasaga tegishli jihozlar
        equipments = RoomsEquipment.objects.filter(organization_for=organization)

        context = {
            'organization': organization,   # Muassasa obyekti
            'admin_profile': admin_profile,  # Admin user_profile
            'base_classes': base_classes,     # Sinflar
            'equipments': equipments,         # Jihozlar
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

class ComposeMessageView(LoginRequiredMixin, View):
    def get(self, request):
        # Agar “odam o‘zidan boshqa hammani ko‘rsin” desangiz:
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
