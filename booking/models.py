from django.db import models
from django.contrib.auth.models import User
import uuid
import json

# Create your models here.
class Flight_Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.UUIDField(default=uuid.uuid4,editable=False, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    flight_id = models.CharField(max_length=5)
    flight_carrierCode = models.CharField(max_length=5)
    no_adults = models.IntegerField(default=1)
    departure_location = models.CharField(max_length=50)
    departure_date = models.DateField()
    departure_time = models.CharField(max_length=20)
    arrival_location = models.CharField(max_length=50)
    arrival_date = models.DateField()
    arrival_time = models.CharField(max_length=20)
    passenger_names = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_currency = models.CharField(max_length=5)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=30, default='Not Available')
    payer_id = models.CharField(max_length=30, default='Not Available')

    def set_passenger_name(self,names_list):
        self.passenger_names = json.dumps(names_list)

    def get_passenger_names(self):
        return json.loads(self.passenger_names)
    
    def __str__(self):
        return f"Flight Booking {self.booking_id} by {self.user.first_name}"

class Hotel_Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.UUIDField(default=uuid.uuid4,editable=False, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    hotel_id = models.CharField(max_length=20)
    hotel_name = models.CharField(max_length=255)
    hotel_city = models.CharField(max_length=5)
    no_rooms = models.IntegerField(default=1)
    check_in = models.DateField()
    check_out =  models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_currency = models.CharField(max_length=5)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=30, default='Not Available')
    payer_id = models.CharField(max_length=30, default='Not Available')

    def __str__(self):
        return f"Hotel Booking {self.booking_id} by {self.user.first_name}"
    