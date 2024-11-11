from django import forms
from organizations.models import EquipmentName

class CreateEquipmentNameForm(forms.ModelForm):
    class Meta:
        model = EquipmentName
        fields = ['name']