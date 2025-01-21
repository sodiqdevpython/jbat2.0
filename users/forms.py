from django import forms
from organizations.models import Message, RoomsEquipment
from django.contrib.auth.models import User
from organizations.models import Message, Organizations

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
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
        super().__init__(*args, **kwargs)
        self.fields['recipient'].label_from_instance = lambda user_obj: (
            getattr(user_obj, 'user_profile', None) 
            and getattr(user_obj.user_profile, 'fio', user_obj.username) 
            or user_obj.username
        )

class RoomsEquipmentForm(forms.ModelForm):
    class Meta:
        model = RoomsEquipment
        fields = [
            'name', 'measure_type', 'amount',
            'avilable_type', 'accepted_date', 'invert_number',
            'entered_date', 'when_first_time_used', 'when_made',
            'image1', 'image2', 'image3',
            'penny_by_year', 'xarakteri', 'equipment_type',
            'command_file'
        ]
        labels = {
            'name': "Jihoz nomi",
            'measure_type': "O'lchov turi",
            'amount': "Miqdor ketma-ketligi",
            'avilable_type': "Jihoz holati",
            'accepted_date': "Qabul qilingan sana",
            'invert_number': "Invert raqami",
            'entered_date': "Kiritilgan sana",
            'when_first_time_used': "Birinchi foydalanilgan sana",
            'when_made': "Ishlab chiqarilgan yil",
            'image1': "Rasm 1",
            'image2': "Rasm 2",
            'image3': "Rasm 3",
            'penny_by_year': "Yillik eskirish foizi",
            'xarakteri': "Jihoz xususiyatlari",
            'equipment_type': "Jihoz turi",
            'command_file': "Buyruq fayli (PDF yoki DOCX)",
        }
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'measure_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.Select(attrs={'class': 'form-control'}),
            'avilable_type': forms.Select(attrs={'class': 'form-control'}),
            'accepted_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'invert_number': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'when_first_time_used': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'when_made': forms.NumberInput(attrs={'class': 'form-control', 'min': 1950, 'max': 2024}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'penny_by_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'xarakteri': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipment_type': forms.Select(attrs={'class': 'form-control'}),
            'command_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_invert_number(self):
        """
        Invert raqam (invert_number) bo‘lmasa, yoki format xato bo‘lsa, shu yerda 
        qo‘shimcha validatsiya qilishingiz mumkin. Modelda unique=True bo‘lgani uchun, 
        takror raqam kiritilsa form xato beradi.
        """
        invert_number = self.cleaned_data.get('invert_number')
        return invert_number

    def __init__(self, *args, **kwargs):
        self.current_user_profile = kwargs.pop('current_user_profile', None)
        super().__init__(*args, **kwargs)
        if self.current_user_profile and self.current_user_profile.user:
            org = Organizations.objects.filter(admin=self.current_user_profile).first()


class EquipmentCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = RoomsEquipment
        fields = [
            'name', 'measure_type', 'amount',
            'avilable_type', 'accepted_date', 'invert_number',
            'entered_date', 'when_first_time_used', 'when_made',
            'image1', 'image2', 'image3',
            'penny_by_year', 'xarakteri', 'equipment_type',
            'command_file'
        ]

        labels = {
            'name': "Jihoz nomi",
            'measure_type': "O'lchov turi",
            'amount': "Miqdor",
            'avilable_type': "Jihoz holati",
            'accepted_date': "Qabul qilingan sana",
            'invert_number': "Invert raqami",
            'entered_date': "Kiritilgan sana",
            'when_first_time_used': "Birinchi foydalanilgan sana",
            'when_made': "Ishlab chiqarilgan yil",
            'image1': "Rasm 1",
            'image2': "Rasm 2",
            'image3': "Rasm 3",
            'penny_by_year': "Yillik eskirish foizi",
            'xarakteri': "Jihoz xususiyatlari",
            'equipment_type': "Jihoz turi",
            'command_file': "Buyruq fayli (pdf/docx)",
        }

        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'measure_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'avilable_type': forms.Select(attrs={'class': 'form-control'}),
            'accepted_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'invert_number': forms.TextInput(attrs={'class': 'form-control'}),
            'entered_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'when_first_time_used': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'when_made': forms.NumberInput(attrs={'class': 'form-control', 'min': 1950, 'max': 2030}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'penny_by_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'xarakteri': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'equipment_type': forms.Select(attrs={'class': 'form-control'}),
            'command_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
