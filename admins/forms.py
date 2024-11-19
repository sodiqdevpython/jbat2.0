from django import forms
from django.contrib.auth.models import User
from organizations.models import EquipmentName, Organizations, UserProfile

class CreateEquipmentNameForm(forms.ModelForm):
    class Meta:
        model = EquipmentName
        fields = ['name']