from django.contrib import admin
from booking.models import Hotel_Booking, Flight_Booking

# Register your models here.
admin.site.register(Hotel_Booking)
admin.site.register(Flight_Booking)
