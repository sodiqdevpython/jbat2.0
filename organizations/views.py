from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import LoginForm, ContactForm, UserProfileForm, OrganizationForm, MessageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FAQ, UserProfile, Organizations, BaseClasses, RoomsEquipment, Message
from django.contrib.auth.models import User
from django.core.paginator import Paginator


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
                # Foydalanuvchi roliga qarab yo'naltirish
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

    
class UserDetail(View):
    def get(self, request, id):
        user_profile = get_object_or_404(UserProfile, id=id)
        organization = Organizations.objects.filter(admin=user_profile).first()
        base_classes = BaseClasses.objects.filter(author=user_profile)
        equipments = RoomsEquipment.objects.filter(author=user_profile)
        
        context = {
            'user_profile': user_profile,
            'organization': organization,
            'base_classes': base_classes,
            'equipments': equipments
        }
        return render(request, 'admins/user-detail.html', context)
    

class OrganizationDetail(View):
    def get(self, request, id):
        organization = get_object_or_404(Organizations, id=id)
        base_classes = BaseClasses.objects.filter(organization=organization)
        equipments = RoomsEquipment.objects.filter(organization_for=organization)
        admin_profile = organization.admin
        
        context = {
            'organization': organization,
            'base_classes': base_classes,
            'equipments': equipments,
            'admin_profile': admin_profile
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

            return redirect('organization_list')

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