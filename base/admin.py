from django.contrib import admin

# Register your models here.

from . import models 

# Custom admin for ReservationSlot
class ReservationSlotAdmin(admin.ModelAdmin):
    list_display = ('unit_id_display', 'start_time', 'end_time', 'status', 'display_unit_category','display_slot_reservation')
    list_filter = ('status', 'unit__belongs_to_category__category_name')

    def unit_id_display(self, obj): 
        return obj.unit.id
    unit_id_display.short_description = 'Unit ID'  # This sets a nicer header for the column
    
    
    def display_unit_category(self, obj):
        return obj.unit.belongs_to_category.category_name
    display_unit_category.short_description = 'Category'

    def display_slot_reservation(self, obj):
        if obj.reservation:
            return obj.reservation.reservation_from
        else:
            return "-"
    display_unit_category.short_description = 'Reservation'




# Register your models here
admin.site.register(models.ReservationSlot, ReservationSlotAdmin)

# admin.site.register(models.Assigned)
#admin.site.register(models.UserRole)
admin.site.register(models.Offer)
admin.site.register(models.Pricing)
admin.site.register(models.Reservation)
admin.site.register(models.Category)
admin.site.register(models.Unit)
admin.site.register(models.ManagerProfile)
#admin.site.register(models.ReservationSlot)