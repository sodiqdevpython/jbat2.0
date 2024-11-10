from django import forms
from .models import Contact 

class LoginForm(forms.Form):
    username = forms.CharField(max_length=9)
    password = forms.CharField(widget=forms.PasswordInput)

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'tel_number', 'body']