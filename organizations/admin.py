from django.contrib import admin
from .models import (
    Regions, Districts, Cities, Organizations, EquipmentName,
    RoomsEquipment, OrganizationStatistics, Professions, UserProfile,
    Message, FAQ, Contact
)

@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "updated", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)

@admin.register(Districts)
class DistrictsAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "created", "updated", "is_active")
    search_fields = ("name", "region__name")
    list_filter = ("region", "is_active")
    ordering = ("name",)

@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "created", "updated", "is_active")
    search_fields = ("name", "region__name")
    list_filter = ("region", "is_active")
    ordering = ("name",)

@admin.register(Organizations)
class OrganizationsAdmin(admin.ModelAdmin):
    list_display = (
        "name", "organization_number", "education_type",
        "region", "district", "city", "is_inclusive",
        "students_amount", "power", "ball", "admin",
        "created", "updated", "is_active"
    )
    search_fields = (
        "name", "admin__first_name", "admin__last_name",
        "region__name", "district__name", "city__name"
    )
    list_filter = (
        "education_type", "is_inclusive",
        "region", "district", "city",
        "is_active"
    )
    ordering = ("-created",)

@admin.register(EquipmentName)
class EquipmentNameAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "updated", "is_active")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(RoomsEquipment)
class RoomsEquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "measure_type", "amount", "avilable_type",
        "invert_number", "entered_date", "equipment_type",
        "organization_for", "author", "created", "updated", "is_active"
    )
    search_fields = (
        "name__name",      # Jihoz nomi (EquipmentName)
        "invert_number", 
        "author__first_name", "author__last_name",
        "organization_for__name"
    )
    list_filter = (
        "measure_type", "avilable_type", "equipment_type",
        "organization_for", "is_active"
    )
    ordering = ("-created",)

@admin.register(OrganizationStatistics)
class OrganizationStatisticsAdmin(admin.ModelAdmin):
    list_display = ("type", "number", "created", "updated", "is_active")
    search_fields = ("type",)
    ordering = ("type",)

@admin.register(Professions)
class ProfessionsAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "updated", "is_active")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "first_name", "last_name", "passport_id",
        "tel_number", "position", "is_selected",
        "created", "updated", "is_active"
    )
    search_fields = ("first_name", "last_name", "passport_id", "pinfl")
    list_filter = ("position", "is_selected", "is_active")
    ordering = ("-created",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "subject", "timestamp", "is_read")
    search_fields = ("subject", "sender__username", "recipient__username")
    list_filter = ("is_read", "timestamp")
    ordering = ("-timestamp",)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("title", "body")
    search_fields = ("title", "body")
    ordering = ("title",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "tel_number", "body", "created")
    search_fields = ("name", "tel_number", "body")
    ordering = ("-created",)
