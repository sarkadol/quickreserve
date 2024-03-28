from django.contrib import admin

# Register your models here.

from . import models 



# Custom admin for ReservationSlot
class ReservationSlotAdmin(admin.ModelAdmin):
    list_display = ('unit', 'start_time', 'end_time', 'status', 'display_unit_category')
    list_filter = ('status', 'unit__belongs_to_category__category_name')
    
    def display_unit_category(self, obj):
        return obj.unit.belongs_to_category.category_name
    display_unit_category.short_description = 'Category'

# Register your models here
admin.site.register(models.ReservationSlot, ReservationSlotAdmin)
# Register other models as needed, potentially with custom ModelAdmin classes

# admin.site.register(models.Assigned)
admin.site.register(models.UserRole)
admin.site.register(models.Offer)
admin.site.register(models.Pricing)
admin.site.register(models.Reservation)
admin.site.register(models.Category)
admin.site.register(models.Unit)
#admin.site.register(models.ReservationSlot)