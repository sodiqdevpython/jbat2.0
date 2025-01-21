from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import LoginForm, ContactForm, UserProfileForm, OrganizationForm, MessageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FAQ, UserProfile, Organizations, RoomsEquipment, Message
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import date, timedelta


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin_dashboard')  # Admin uchun dashboard
            else:
                return redirect('user_dashboard')  # Oddiy foydalanuvchi uchun dashboard
        return render(request, 'org/auth/login.html')

    def post(self, request):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            get_data = form.cleaned_data
            user = authenticate(request, username=get_data['username'], password=get_data['password'])
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Admin uchun dashboard
                else:
                    return redirect('user_dashboard')  # Oddiy foydalanuvchi uchun dashboard
            else:
                error_message = "ID raqam yoki parol xato !"

                context = {
                    'form': form,
                    'error_message': error_message
                }
                return render(request, 'org/auth/login.html', context)
        else:
            error_message = "Ma'lumotlar to'liq va to'g'ri kiritilishi shart!"
            return render(request, 'org/auth/login.html', {'form': form, 'error_message': error_message})

class LogoutView(View, LoginRequiredMixin):
    def get(self, request):
        logout(request)
        return redirect('login')


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

class UserDetail(View):
    def get(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        organization = Organizations.objects.filter(admin=user_profile).first()

        user_equipments = RoomsEquipment.objects.filter(author=user_profile).order_by('-created')
        paginator = Paginator(user_equipments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        months_count = 6
        from datetime import date, timedelta
        today = date.today()
        months = [
            (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            for i in range(months_count)
        ]
        months = sorted(months)
        monthly_equipment_data = []
        for m in months:
            monthly_equipment_data.append(
                user_equipments.filter(entered_date__year=m.year, entered_date__month=m.month).count()
            )
        equipment_history = []
        for eq in user_equipments:
            eq_hist = eq.history.filter(history_type='+').order_by('-history_date')
            for h in eq_hist:
                equipment_history.append(h)
        equipment_history.sort(key=lambda x: x.history_date, reverse=True)

        sent_messages = Message.objects.filter(sender=user_profile.user).order_by('-timestamp')

        django_user_obj = user_profile.user 

        context = {
            "user_profile": user_profile,
            "organization": organization,
            "page_obj": page_obj,
            "months_list": [m.strftime("%b %Y") for m in months],
            "monthly_equipment_data": monthly_equipment_data,
            "equipment_history": equipment_history,
            "sent_messages": sent_messages,
            "django_user": django_user_obj
        }
        return render(request, 'admins/user-detail.html', context)
    
class OrganizationDetail(View):
    def get(self, request, id):
        organization = get_object_or_404(Organizations, id=id)

        all_equipments = RoomsEquipment.objects.filter(organization_for=organization).order_by('-created')

        page_number = request.GET.get('page', 1)
        paginator = Paginator(all_equipments, 10)
        page_obj = paginator.get_page(page_number)

        months_count = 6
        today = date.today()
        months = [
            (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            for i in range(months_count)
        ]
        months = sorted(months)
        monthly_equipment_data = []
        for m in months:
            c = all_equipments.filter(
                entered_date__year=m.year, 
                entered_date__month=m.month
            ).count()
            monthly_equipment_data.append(c)

        equipment_history = []
        for eq in all_equipments:
            eq_hist = eq.history.filter(history_type='+').order_by('-history_date')
            for h in eq_hist:
                equipment_history.append(h)
        equipment_history.sort(key=lambda x: x.history_date, reverse=True)

        total_equipment = all_equipments.count()
        student_count = organization.students_amount

        context = {
            'organization': organization,
            'page_obj': page_obj,
            'months_list': [m.strftime("%b %Y") for m in months],
            'monthly_equipment_data': monthly_equipment_data,
            'equipment_history': equipment_history,
            'total_equipment': total_equipment,
            'student_count': student_count
        }
        return render(request, 'admins/organization-detail.html', context)

class CreateUserProfileOrganization(View):
    def get(self, request):
        user_profile_form = UserProfileForm()
        organization_form = OrganizationForm()
        context = {
            'user_profile_form': user_profile_form,
            'organization_form': organization_form,
        }
        return render(request, 'admins/create_user_profile_org.html', context)

    def post(self, request):
        user_profile_form = UserProfileForm(request.POST, request.FILES)
        organization_form = OrganizationForm(request.POST)

        if user_profile_form.is_valid() and organization_form.is_valid():
            user_profile = user_profile_form.save(commit=False)
            password = user_profile_form.cleaned_data['password']
            passport_id = user_profile_form.cleaned_data['passport_id']

            user = User.objects.create_user(
                username=passport_id,
                password=password
            )
            user_profile.user = user
            user_profile.save()

            organization = organization_form.save(commit=False)
            organization.admin = user_profile
            organization.save()

            user_profile.is_selected = True
            user_profile.save()

            messages.success(request, "Yangi foydalanuvchi va muassasa muvaffaqiyatli qo'shildi!")
            return redirect('organization_list')
        else:
            messages.error(request, "Iltimos, shakldagi xatolarni to‘g‘rilang.")

        context = {
            'user_profile_form': user_profile_form,
            'organization_form': organization_form,
        }
        return render(request, 'admins/create_user_profile_org.html', context)     
        


class InboxView(LoginRequiredMixin, View):
    def get(self, request):
        messages_list = Message.objects.filter(recipient=request.user).order_by('-timestamp')
        paginator = Paginator(messages_list, 10)
        page_number = request.GET.get('page')
        messages = paginator.get_page(page_number)
        context = {
            'messages': messages
        }
        return render(request, 'messages/inbox.html', context)

class SentView(LoginRequiredMixin, View):
    def get(self, request):
        messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
        context = {
            'messages': messages
        }
        return render(request, 'messages/sent.html', context)

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
        return render(request, 'messages/message_detail.html', context)

class ComposeMessageView(LoginRequiredMixin, View):
    def get(self, request):
        form = MessageForm(current_user=request.user)
        return render(request, 'messages/compose.html', {'form': form})
    
    def post(self, request):
        form = MessageForm(request.POST, current_user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('sent')
        return render(request, 'messages/compose.html', {'form': form})
    
class EquipmentDetailView(LoginRequiredMixin, View):
    template_name = "admins/org/equipment_detail.html"

    def get(self, request, pk):
        equipment = get_object_or_404(RoomsEquipment, pk=pk)

        context = {
            'equipment': equipment
        }
        return render(request, self.template_name, context)
    

from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import RoomsEquipmentSerializer, OrganizationsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RoomsEquipmentReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    Ushbu ViewSet faqat GET (list va retrieve) amallarini taqdim etadi.
    POST, PUT, PATCH, DELETE - ruxsat berilmaydi.
    """
    queryset = RoomsEquipment.objects.all()
    serializer_class = RoomsEquipmentSerializer


class OrganizationsReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Organizations.objects.all()
    serializer_class = OrganizationsSerializer
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_fields = ['is_inclusive', 'region', 'district', 'city', 'education_type']
    search_fields = ['name', 'organization_number']
    ordering_fields = ['created', 'updated', 'students_amount', 'power', 'ball']
    ordering = ['-created']