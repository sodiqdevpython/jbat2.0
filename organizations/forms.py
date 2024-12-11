from django import forms
from .models import Contact, UserProfile, Organizations, Regions, Cities, Districts, Message
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=9)
    password = forms.CharField(widget=forms.PasswordInput)

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'tel_number', 'body']

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parolni kiriting'}),
    )
    command_expire = forms.DateField(
        label="Buyruq tugash vaqti",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    command_pdf = forms.FileField(
        label="Buyruq fayli (pdf/docx)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'born_in', 'father_name', 'passport_id',
            'manzil', 'pinfl', 'position', 'tel_number', 'command_expire', 'command_pdf'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ism'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Familiya'}),
            'born_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Otasining ismi'}),
            'passport_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pasport ID'}),
            'manzil': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Manzil'}),
            'pinfl': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PINFL'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'tel_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon raqam'}),
        }
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'born_in': 'Tug‘ilgan sana',
            'father_name': 'Otasining ismi',
            'passport_id': 'Pasport ID',
            'manzil': 'Manzil',
            'pinfl': 'PINFL',
            'position': 'Lavozim',
            'tel_number': 'Telefon raqam',
            'command_expire': "Buyruq tugash vaqti",
            'command_pdf': "Buyruq fayli",
        }

class OrganizationForm(forms.ModelForm):
    is_inclusive = forms.ChoiceField(
        choices=[('True', 'Ha'), ('False', 'Yo‘q')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Inclusive",
        required=True
    )
    region = forms.ModelChoiceField(
        queryset=Regions.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Viloyat",
        required=True
    )
    location_type = forms.ChoiceField(
        choices=[('city', 'Shahar'), ('district', 'Tuman')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Joylashuv turi",
        required=True
    )
    city = forms.ModelChoiceField(
        queryset=Cities.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Shahar",
        required=False
    )
    district = forms.ModelChoiceField(
        queryset=Districts.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tuman",
        required=False
    )

    class Meta:
        model = Organizations
        fields = [
            'organization_number', 'name', 'education_type', 'power', 'is_inclusive', 
            'rating', 'students_amount', 'ball', 'latitude', 'longitude', 'region', 'city', 'district'
        ]
        widgets = {
            'organization_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Muassasa raqami'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tashkilot nomi'}),
            'education_type': forms.Select(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quvvat'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'students_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Talabalar soni'}),
            'ball': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ball'}),
            'latitude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kenglik'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Uzunlik'}),
        }
        labels = {
            'organization_number': 'Muassasa raqami',
            'name': 'Tashkilot nomi',
            'education_type': 'Tashkilot turi',
            'power': 'Quvvat',
            'rating': 'Reyting',
            'students_amount': 'Talabalar soni',
            'ball': 'Ball',
            'latitude': 'Kenglik (latitude)',
            'longitude': 'Uzunlik (longitude)',
        }

    def clean_is_inclusive(self):
        val = self.cleaned_data['is_inclusive']
        return True if val == 'True' else False

    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get('location_type')
        city = cleaned_data.get('city')
        district = cleaned_data.get('district')

        if location_type == 'city' and not city:
            self.add_error('city', "Shahar tanlang")
        elif location_type == 'district' and not district:
            self.add_error('district', "Tuman tanlang")

        return cleaned_data


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Qabul qiluvchi",
        required=True
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mavzu'}),
        label="Mavzu",
        required=True
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Xabaringizni yozing...'}),
        label="Xabar",
        required=True
    )
    
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        if current_user:
            if current_user.is_superuser:
                self.fields['recipient'].queryset = User.objects.all().exclude(id=current_user.id)
            else:
                admin_users = User.objects.filter(is_superuser=True)
                self.fields['recipient'].queryset = admin_users
                if admin_users.count() == 1:
                    self.initial['recipient'] = admin_users.first()
                    self.fields['recipient'].widget = forms.HiddenInput()
            
            self.fields['recipient'].label_from_instance = lambda obj: obj.user_profile.fio