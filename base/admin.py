from django.contrib import admin

# Register your models here.

from . import models 

# admin.site.register(models.Assigned)
admin.site.register(models.UserRole)
admin.site.register(models.Offer)
admin.site.register(models.Pricing)
admin.site.register(models.Reservation)
admin.site.register(models.Unit)



