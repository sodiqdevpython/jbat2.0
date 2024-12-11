from django.db import models
from utils.models import BaseModel
from django.contrib.auth.models import User
from utils.choice import OrganizationsType, OrganizationsRatingType,MeasureType, EquipmentType, AvilableType
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator


#! Viloay uchun model

class Regions(BaseModel):
    name = models.CharField(max_length=32, unique=True, validators=[MinLengthValidator(limit_value=6, message="Viloyat nomi juda qisqa, noto'g'ri kiritgansiz")])

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
        ordering = ['name']

#! /Viloyat uchun model


#! Tuman uchun model

class Districts(BaseModel):
    region = models.ForeignKey(Regions, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True, validators=[MinLengthValidator(limit_value=5, message="Tuman nomi juda qisqa, noto'g'ri kiritgansiz")])

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"

#! /Tuman uchun model


#! Shaxar uchun model

class Cities(BaseModel):
    region = models.ForeignKey(Regions, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True, validators=[MinLengthValidator(limit_value=5, message="Shaxar nomi juda qisqa, noto'g'ri kiritgansiz")])

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Shaxar"
        verbose_name_plural = "Shaxarlar"

#! Shaxar uchun model


#! Muassasa

class Organizations(BaseModel):
    organization_number = models.PositiveIntegerField()
    name = models.CharField(max_length=64, validators=[MinLengthValidator(limit_value=5, message="Muassasa nomi juda qisqa, noto'g'ri kiritgansiz")])
    education_type = models.CharField(max_length=32, choices=OrganizationsType.choices)
    power = models.PositiveBigIntegerField(default=0)
    is_inclusive = models.BooleanField(default=False)
    rating = models.CharField(max_length=16, choices=OrganizationsRatingType.choices, null=True, blank=True)

    district = models.ForeignKey(Districts, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, null=True, blank=True)
    
    region = models.ForeignKey(Regions, on_delete=models.CASCADE)

    students_amount = models.PositiveBigIntegerField(default=0)

    ball = models.PositiveBigIntegerField(default=0)

    latitude = models.CharField(max_length=32)
    longitude = models.CharField(max_length=32)

    admin = models.OneToOneField("organizations.UserProfile", on_delete=models.SET_NULL, null=True, blank=True)

    is_selected = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.admin:
            self.admin.is_selected = True
            self.admin.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Muassasa"
        verbose_name_plural = "Muassasa"
        ordering = ['-ball']

#! / Muassasa


#! Umumiy sinf turlari

class BaseClassCategory(BaseModel):
    name = models.CharField(max_length=512, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Umumiy sinf turi"
        verbose_name_plural = "Umumiy sinf turlari"

#! /Umumiy sinf turlari


#! Umumiy sinf subtitle 

class BaseClassSubtitle(BaseModel):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Umumiy sinf subtitle"
        verbose_name_plural = "Umumiy sinf subtitles"

#! /Umumiy sinf subtitle 


#! Umumiy sinflar

class BaseClasses(BaseModel):
    organization = models.ForeignKey('organizations.Organizations', on_delete=models.CASCADE)
    name = models.ForeignKey(BaseClassCategory, on_delete=models.SET_NULL, null=True, blank=True)
    subtitle = models.ForeignKey(BaseClassSubtitle, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey('organizations.UserProfile', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.name.name)
    
    class Meta:
        verbose_name = "Umumiy sinf"
        verbose_name_plural = "Umumiy sinflar"
        unique_together = ['organization', 'name']

#! /Umumiy sinflar

#! Sinf xonadagi o'quvchilar sig'imi va ajratilgan jihozlar soni ketma ketligi

class AmountSelect(BaseModel):
    first = models.CharField(max_length=128, unique=True)
    second = models.CharField(max_length=256 ,unique=True)

    def __str__(self):
        return f"{self.first} | {self.second}"

#! Sinf xonadagi o'quvchilar sig'imi va ajratilgan jihozlar soni ketma ketligi

class EquipmentName(BaseModel):
    name = models.CharField(max_length=1024, validators=[MinLengthValidator(3, "Jihoz nomi juda qisqa, xato kiritgan bo'lishingiz mumkin !")], unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Jihoz nomi"
        verbose_name_plural = "Jihozlar nomlari"
#! Xona jihozlari

class RoomsEquipment(BaseModel):
    name = models.ForeignKey(EquipmentName, on_delete=models.SET_NULL, null=True)
    measure_type = models.CharField(max_length=8, choices=MeasureType.choices)
    amount = models.ForeignKey(AmountSelect, on_delete=models.SET_NULL, null=True, blank=True) # shu jihozdan nechtaligi

    avilable_type = models.CharField(max_length=32, choices=AvilableType.choices)

    accepted_date = models.DateField() # bu jihoz(lar) qachon olib kelingan

    invert_number = models.CharField(max_length=128, unique=True) #invert raqam

    entered_date = models.DateField() # bu jihoz qachon kirim qilindi

    when_first_time_used = models.DateField() #qachon_foydalanildi

    when_made = models.PositiveIntegerField(validators=[MinValueValidator(1950), MaxValueValidator(2024)], null=True, blank=True) #shu_jihoz_qachon_ishlab_chiqarilganligi

    
    image1 = models.ImageField(upload_to='school/rooms/equipement/', null=True, blank=True)
    image2 = models.ImageField(upload_to='school/rooms/equipement/', null=True, blank=True)
    image3 = models.ImageField(upload_to='school/rooms/equipement/', null=True, blank=True)

    penny_by_year = models.FloatField() # yiliga qancha foiz eskirish foizi

    xarakteri = models.TextField(null=True, blank=True)

    equipment_type = models.CharField(max_length=16, choices=EquipmentType.choices)

    room = models.ForeignKey(BaseClasses, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_room')

    author = models.ForeignKey('organizations.UserProfile', on_delete=models.SET_NULL, null=True, blank=True)

    organization_for = models.ForeignKey(Organizations, on_delete=models.SET_NULL, null=True)

    command_file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'], message="Faqat pdf yoki docx formatda fayl yulay olasiz")])

    def __str__(self):
        return str(self.name.name)
    
    class Meta:
        verbose_name = "Xona jihozi"
        verbose_name_plural = "Xonalar jihozlari"
    

#! SchoolStatistics

class OrganizationStatistics(BaseModel):
    type = models.CharField(max_length=32, choices=OrganizationsType.choices, unique=True)
    number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = "Tashkilot turi"
        verbose_name_plural = "Tashkilot turlari"

#! /SchoolStatistics

class Professions(BaseModel):
    name = models.CharField(max_length=512, unique=True)

    def __str__(self):
        return self.name

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='user_profile')
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    born_in = models.DateField()
    father_name = models.CharField(max_length=32)
    passport_id = models.CharField(max_length=9, unique=True)
    manzil = models.CharField(max_length=512)
    pinfl = models.CharField(max_length=14, unique=True)
    position = models.ForeignKey(Professions, on_delete=models.SET_NULL, null=True)
    tel_number = models.CharField(max_length=9)

    command_expire = models.DateField(null=True, blank=True) # buyruq tugash vaqti
    command_pdf = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]) # pdf file Buyrug' (Moddiy texnik baza bo'yicha mas'ul shaxs buyrug'i)

    is_selected = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def fio(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def get_uuid(self):
        return self.id

    class Meta:
        verbose_name = "Foydalanuvchi profili"
        verbose_name_plural = "Foydalanuvchilar profillari"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"From {self.sender} to {self.recipient}: {self.subject}"


#! Public uchun

class FAQ(models.Model):
    title = models.CharField(max_length=64, unique=True)
    body = models.CharField(max_length=512)

    def __str__(self):
        return self.title
    

class Contact(models.Model):
    name = models.CharField(max_length=32)
    tel_number = models.CharField(max_length=13)
    body = models.TextField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name