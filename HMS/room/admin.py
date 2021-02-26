from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Dependees)
admin.site.register(RoomServices)
admin.site.register(Refund)
