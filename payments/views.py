from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import paypalrestsdk
from django.urls import reverse
from django.http import HttpResponse
from booking.models import Hotel_Booking,Flight_Booking
from django.views.decorators.csrf import csrf_exempt
from .ticket_gen import generate_pdf
from django.conf import settings
from django.core.mail import EmailMessage

paypalrestsdk.configure({
  "mode": "sandbox",  
  "client_id": "*******************",
  "client_secret": "*******************"
})

# Create your views here.
@login_required
def payment_page(request, booking_id, booking_type):
    if booking_type == 'hotel':
        booking = get_object_or_404(Hotel_Booking, booking_id=booking_id)
        request.session['booking_type'] = 'hotel'
    elif booking_type == 'flight':
        booking = get_object_or_404(Flight_Booking, booking_id =  booking_id)
        request.session['booking_type'] = 'flight'
    else:
        return HttpResponse("Proper Booking Type not fetched!")
    
    try:
        return render(request, 'payments/payment.html', {'booking': booking, 'booking_type':booking_type})
    except:
        return HttpResponse("Rendering error "+ booking)


@csrf_exempt
def process_payment(request, booking_id):
    booking_type = request.session.get('booking_type')
    
    paypal_order = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payments:execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payments:cancel_payment'))
        },
    }

    paypal_order["transactions"] = []
    paypal_order["transactions"].append({})
    paypal_order["transactions"][0]["item_list"] = {}
    paypal_order["transactions"][0]["item_list"]["items"] = []
    paypal_order["transactions"][0]["item_list"]["items"].append({})
    paypal_order["transactions"][0]["amount"] = {}


    if booking_type == 'hotel':
        booking = get_object_or_404(Hotel_Booking, booking_id=booking_id)
        paypal_order["transactions"][0]["item_list"]["items"][0]["name"] = booking.hotel_name


    elif booking_type == 'flight':
        booking = get_object_or_404(Flight_Booking, booking_id=booking_id)
        paypal_order["transactions"][0]["item_list"]["items"][0]["name"] = str(booking.departure_location + booking.flight_id)
        
    else:
        return HttpResponse("Proper Object not fetched")
    
    paypal_order["transactions"][0]["item_list"]["items"][0]["sku"] = str(booking.booking_id)
    paypal_order["transactions"][0]["item_list"]["items"][0]["quantity"] = 1
    paypal_order["transactions"][0]["item_list"]["items"][0]["price"] = str(booking.total_amount)
    paypal_order["transactions"][0]["item_list"]["items"][0]["currency"] = 'USD'
    paypal_order["transactions"][0]["amount"]["total"] = str(booking.total_amount)
    paypal_order["transactions"][0]["amount"]["currency"] = 'USD'

    paypal_order["transactions"][0]["description"] = f"Booking by {request.user.username}"

    payment = paypalrestsdk.Payment(paypal_order)

    if payment.create():
        for link in payment.links:   
            if link.rel == 'approval_url':
                redirect_url = str(link.href)
                return redirect(redirect_url)
    else:
        return render(request, 'payments/payment_error.html', {'error': payment.error})

    return render(request, 'payments/payment_error.html', {'error': 'An unknown error occurred'})


@csrf_exempt
def execute_payment(request):
    booking_type = request.session.get('booking_type')

    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        booking_id = payment.transactions[0].item_list.items[0].sku

        if booking_type == 'hotel':
            booking = Hotel_Booking.objects.get(booking_id=booking_id)
        elif booking_type == 'flight':
            booking = Flight_Booking.objects.get(booking_id=booking_id)
        else:
            return HttpResponse("Session Storage error!")
        
        booking.payment_status = True
        booking.payment_id = payment_id
        booking.payer_id = payer_id
        booking.save()
        pdf = generate_pdf(booking_type=booking_type,booking_id=booking_id)
        filename = f'Booking-{booking_type}-{booking_id}.pdf'

        if pdf:
            subject = f'Booking for {booking_type} by {request.user.username} with Ticket PDF'
            message = 'Thankyou for booking from Tourify, Please Find the attacked Ticket PDF document.'
            email_from = settings.DEFAULT_FROM_EMAIL
            user_email = request.user.email
            recipient_list = [user_email]

            email = EmailMessage(subject,message, email_from, recipient_list)
            email.attach(filename,pdf,'application/pdf')
            email.send()
        else:
            print('Email not sent! pdf not generated!')

        return render(request, 'payments/payment_success.html')
    else:
        return render(request, 'payments/payment_error.html', {'error': payment.error})

def cancel_payment(request):
    return render(request, 'payments/payment_cancelled.html')