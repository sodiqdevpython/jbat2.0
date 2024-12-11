from django.contrib import admin
from .models import *

admin.site.register(Regions)
admin.site.register(Districts)
admin.site.register(Cities)
admin.site.register(Organizations)
admin.site.register(BaseClassCategory)
admin.site.register(BaseClassSubtitle)
admin.site.register(BaseClasses)
admin.site.register(AmountSelect)
admin.site.register(RoomsEquipment)
admin.site.register(OrganizationStatistics)
admin.site.register(UserProfile)
admin.site.register(Professions)
admin.site.register(EquipmentName)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')

# Public

admin.site.register(FAQ)
admin.site.register(Contact)