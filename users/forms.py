from django import forms
from organizations.models import Message
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.models import User
from .models import Message

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),  # "Hamma" foydalanuvchilar ko'rinsin
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
        """ current_user argumenti bo'lmasa ham xato chiqmasin. 
            Yoki xohlasangiz, superuser va oddiy userlar ro'yxatini farqlay olasiz.
        """
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Agar ro'yxatni cheklash yoki current_user ni bekor qilmoqchi bo'lsangiz, shunday qoldirishingiz mumkin.
        # If you want simpler logic = show "hamma", then do nothing else.

        # Agar har safar username o‘rniga user_profile.fio ko‘rsatmoqchi bo‘lsangiz, xato chiqmasligi uchun shunday yozish mumkin:
        self.fields['recipient'].label_from_instance = lambda user_obj: (
            getattr(user_obj, 'user_profile', None) 
            and getattr(user_obj.user_profile, 'fio', user_obj.username) 
            or user_obj.username
        )
