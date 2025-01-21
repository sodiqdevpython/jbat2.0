from django import forms
from organizations.models import EquipmentName, UserProfile, Regions, Organizations, Cities, Districts

class CreateEquipmentNameForm(forms.ModelForm):
    class Meta:
        model = EquipmentName
        fields = ['name']

class UserProfileUpdateForm(forms.ModelForm):
    born_in = forms.DateField(
        label='Tug‘ilgan sana',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
        input_formats=['%Y-%m-%d', '%Y/%m/%d'],
        required=True
    )

    command_expire = forms.DateField(
        label='Buyruq tugash vaqti',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
        input_formats=['%Y-%m-%d', '%Y/%m/%d'],
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'father_name',
            'born_in', 'passport_id', 'manzil',
            'pinfl', 'position', 'tel_number',
            'command_expire', 'command_pdf',
        ]
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'father_name': 'Otasining ismi',
            'born_in': 'Tug‘ilgan sana',
            'passport_id': 'Pasport raqami',
            'manzil': 'Yashash manzili',
            'pinfl': 'PINFL',
            'position': 'Lavozim',
            'tel_number': 'Telefon raqami',
            'command_expire': 'Buyruq tugash vaqti',
            'command_pdf': 'Buyruq fayli (pdf/docx)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ismingizni kiriting',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiyangizni kiriting',
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Otasining ismini kiriting',
            }),
            'passport_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AA1234567',
                'maxlength': '9',
            }),
            'manzil': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Tuman/Shahar, ko‘cha, uy raqami...',
            }),
            'pinfl': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '14 xonali raqam',
                'maxlength': '14',
            }),
            'position': forms.Select(attrs={
                'class': 'form-control',
            }),
            'tel_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '901234567',
                'maxlength': '9',
            }),
            'command_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
            }),
        }

class OrganizationUpdateForm(forms.ModelForm):
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
    # Masalan, rating ni tahrirlash paytida ham ko‘rsatmoqchisiz:
    RATING_CHOICES = [
        ('Qoniqarsiz', 'Qoniqarsiz'),
        ('O‘rtacha', 'O‘rtacha'),
        ('Yaxshi', 'Yaxshi')
    ]
    rating = forms.ChoiceField(
        choices=[('', 'Tanlanmagan')] + RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Reyting"
    )

    class Meta:
        model = Organizations
        fields = [
            'organization_number', 'name', 'education_type',
            'power', 'is_inclusive', 'rating',
            'students_amount', 'latitude', 'longitude',
            'region', 'location_type', 'city', 'district'
        ]
        widgets = {
            'organization_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Muassasa raqami'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tashkilot nomi'}),
            'education_type': forms.Select(attrs={'class': 'form-control'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quvvat'}),
            'students_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Sig'imi"}),
            'latitude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kenglik'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Uzunlik'}),
        }
        labels = {
            'organization_number': 'Muassasa raqami',
            'name': 'Tashkilot nomi',
            'education_type': 'Tashkilot turi',
            'power': 'Quvvat',
            'students_amount': 'Talabalar soni',
            'latitude': 'Kenglik (latitude)',
            'longitude': 'Uzunlik (longitude)',
        }

    def clean_is_inclusive(self):
        """'True'/'False' => bool"""
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