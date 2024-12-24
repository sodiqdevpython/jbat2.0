from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from organizations.models import Organizations

class UserDashboardView(LoginRequiredMixin, View):
    template_name = "users/dashboard.html"

    def get(self, request):
        user = request.user
        # Ushbu foydalanuvchiga biriktirilgan tashkilot
        # Agar har bir userga bitta organization biriktirilgan deb faraz qilsak:
        organization = Organizations.objects.filter(admin__user=user).first()

        context = {}
        if organization:
            # Ma'lumotlar va statistika
            # Masalan: rating, students_amount, ball, viloyat, shahar, tuman, va h.k.
            context['organization'] = organization
            context['org_name'] = organization.name
            context['org_rating'] = organization.rating
            context['org_students'] = organization.students_amount
            context['org_ball'] = organization.ball
            context['org_region'] = organization.region.name if organization.region else "Noma'lum"
            context['org_city'] = organization.city.name if organization.city else "Noma'lum"
            context['org_district'] = organization.district.name if organization.district else "Noma'lum"
            context['org_inclusive'] = "Ha" if organization.is_inclusive else "Yo'q"
            # Qo‘shimcha statistika yoki ko‘rsatkichlar kerak bo‘lsa shu yerda tayyorlab olish mumkin.
        else:
            # Agar tashkilot topilmasa
            context['no_organization'] = True

        return render(request, self.template_name, context)

def read(request):
    return render(request, 'users/read.html')

def add(request):
    return render(request, 'users/add.html')