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

# Public

admin.site.register(FAQ)
admin.site.register(Contact)