from django.contrib import admin
from .models import CustomUser, Room,Booking

admin.site.register(CustomUser)
admin.site.register(Room)
admin.site.register(Booking)
# Register your models here.