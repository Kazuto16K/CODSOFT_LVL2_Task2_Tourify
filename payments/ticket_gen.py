from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from booking.models import Hotel_Booking,Flight_Booking


def generate_pdf(booking_type,booking_id):
    if booking_type == 'hotel':
        booking = get_object_or_404(Hotel_Booking,booking_id =  booking_id,payment_status = 1)
        booking_data = {
            'booking_type':'hotel',
            'hotel_name':booking.hotel_name,
            'hotel_city':booking.hotel_city,
            'no_rooms' : booking.no_rooms,
            'check_in': booking.check_in,
            'check_out' : booking.check_out,
        }
    elif booking_type == 'flight':
        booking = get_object_or_404(Flight_Booking,booking_id =  booking_id,payment_status = 1)
        booking_data = {
            'booking_type':'flight',
            'flight_carrierCode':booking.flight_carrierCode,
            'no_adults':booking.no_adults,
            'departure_location': booking.departure_location,
            'departure_date':booking.departure_date,
            'arrival_location':booking.arrival_location,
            'arrival_date':booking.arrival_date,
            'range_of_adults': range(booking.no_adults),
            'passenger_names': booking.get_passenger_names(),
        }
    else:
        return HttpResponse("Invalid Booking Type")
    
    booking_data['booking_id'] = str(booking.booking_id)
    booking_data['booking_date'] = booking.booking_date
    booking_data['booking_name'] = booking.user
    booking_data['payment_id'] = booking.payment_id
    booking_data['payment_amount'] = str(booking.total_amount)
    booking_data['amount_currency'] = booking.amount_currency

    if booking_data:
        pdf = render_pdf(booking_data=booking_data)
        return pdf
    else:
        return HttpResponse("Some error occured! data not fetched!")
        
    

def render_pdf(booking_data:dict):
    template_path = 'ticket/ticket.html'
    template = get_template(template_path)
    html = template.render(booking_data)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")),response)
    if not pdf.err:
        return response.getvalue()
    else:
        return None