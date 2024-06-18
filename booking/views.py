
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import amadeus
from amadeus import Client, ResponseError
from django.contrib import messages
import json
from .models import Flight_Booking,Hotel_Booking
from payments.ticket_gen import generate_pdf

amadeus = Client(
    client_id='*************',   
    client_secret='**********'    
)



# Create your views here.


@login_required 
def home(request):
    return render(request, 'booking/home.html',{'User': request.user})

@login_required
def get_profile(request,username):
    hotel_bookings = Hotel_Booking.objects.filter(user = request.user,payment_status=1)
    flight_bookings = Flight_Booking.objects.filter(user = request.user,payment_status=1)
    return render(request,'booking/profile.html',{'hotel_bookings':hotel_bookings, 'flight_bookings':flight_bookings, 'user':request.user})

@login_required
def get_pdf(request):
    booking_type = request.GET.get('booking_type')
    booking_id = request.GET.get('booking_id')
    resp = generate_pdf(booking_type=booking_type,booking_id=booking_id)
    return HttpResponse(resp,content_type='application/pdf')


@login_required 
def flight_search(request):
    if request.method == 'POST':
        
        origin = request.POST.get("Origin")
        destination = request.POST.get("Destination")
        departure_date = request.POST.get("Departuredate")
        return_date = request.POST.get("Returndate")
        adults = request.POST.get("People")

        
        kwargs = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max":10,
        }
        print(kwargs)
        
        #if return_date:
        #    kwargs["returnDate"] = return_date

        if origin and destination and departure_date:
            try:
                search_flights = amadeus.shopping.flight_offers_search.get(**kwargs)
                search_flights_returned = []
                response = ""
                
                for flight in search_flights.data:
                    offer = {
                        'id': flight['id'],
                        'price': flight['price']['total'],
                        'itineraries': flight['itineraries']
                    }
                    search_flights_returned.append(offer)
                    response = zip(search_flights_returned, search_flights.data)

                request.session['flight-data'] = json.dumps(search_flights.data)

                return render(
                    request,
                    "booking/flight_listing.html",
                    {
                        "response": response,
                        "origin": origin,
                        "destination": destination,
                        "departureDate": departure_date,
                        "returnDate": return_date,
                        'user':request.user,
                    },
                )
            except ResponseError as error:
                messages.add_message(
                    request, messages.ERROR, error.response.result["errors"][0]["detail"]
                )
                return HttpResponse("Error in fetching Flight Data")
    return HttpResponse("Invalid input data")

@login_required
def hotel_search(request):
    if request.method == 'POST':
        location = request.POST.get('Location')
        no_rooms = request.POST.get('Rooms')
        checkin = request.POST.get('Checkin')
        checkout = request.POST.get('Checkout')

        
        if location and checkin and checkout:
            try:
                hotel_list = amadeus.reference_data.locations.hotels.by_city.get(cityCode = location)
            except:
                return HttpResponse("Could not fetch hotel using Amadeus City Code")
            
            hotel_offers = []
            hotel_ids = []
            for i in hotel_list.data:
                hotel_ids.append(i['hotelId'])

            
            reduced_hotel_ids = hotel_ids[:40]
            kwargs = {
                'hotelIds' : reduced_hotel_ids,
                'checkInDate': checkin,
                'checkOutDate': checkout,
            }
            
            try:
                search_hotels = amadeus.shopping.hotel_offers_search.get(**kwargs)
            except:
                return HttpResponse("Some Error occured while fetching hotel offers")
            
            try:
                for hotel in search_hotels.data:
                    room_info = hotel['offers'][0]['room'].get('typeEstimated',{})
                    offer = {
                        'price': hotel['offers'][0]['price']['total'],
                        'currency': hotel['offers'][0]['price']['currency'],
                        'name': hotel['hotel']['name'],
                        'hotelID': hotel['hotel']['hotelId'],
                        'latitude': hotel['hotel']['latitude'],
                        'longitude': hotel['hotel']['longitude'],
                        'roomDesc': hotel['offers'][0]['room']['description']['text'],
                        'roomCategory': room_info.get('category','N/A'),
                        'roomBeds': room_info.get('beds', 'N/A'),
                        'roomBedType': room_info.get('bedType', 'N/A'),
                    }

                    hotel_offers.append(offer)
                    response = zip(hotel_offers, search_hotels.data)
                
                request.session['hotel-data'] = json.dumps(search_hotels.data)
                request.session['no_rooms'] = no_rooms
                    
                return render(request, 'booking/hotel_listing.html', {
                    'response':response,
                    'location':location,
                    'checkin':checkin,
                    'checkout':checkout,
                    'no_of_rooms':no_rooms,
                    'user':request.user,
                })
                
            except UnboundLocalError:
                messages.add_message(request, messages.ERROR, 'No hotels found by API, try modifying search')
                return HttpResponse("Error in fetching Hotel Data")
            
    return HttpResponse("Error in Input Data")
            
                
@login_required
def hotel_detail(request):
    hotel_data = request.session.get('hotel-data')
    hotel_data_list = json.loads(hotel_data)

    if hotel_data is None:
        return HttpResponse("Some error Occured! Try Again")
    else:
        hotel_id = request.GET.get('hotel_id')

        if hotel_id is None:
            return HttpResponse("Hotel ID not being fetched!")

        for hotel_detail in hotel_data_list:
            if "hotel" in hotel_detail and "hotelId" in hotel_detail["hotel"]:
                if hotel_id == hotel_detail["hotel"]["hotelId"]:
                    hotel_id_detail = hotel_detail
                    break

        try:
            boardType = hotel_id_detail['offers'][0]['boardType']
        except KeyError:
            boardType = 'N/A'

        try:
            policy = hotel_id_detail['offers'][0]['policies']['cancellations'][0]['description']['text']
        except KeyError:
            policy = 'N/A'

        try:
            deposit = hotel_id_detail['offers'][0]['policies']['paymentType']
        except KeyError:
            deposit = 'N/A'

        offer = {
            'hotel_id':hotel_id,
            'hotel_name': hotel_id_detail['hotel']['name'],
            'cityCode': hotel_id_detail['hotel']['cityCode'],
            'latitude': hotel_id_detail['hotel']['latitude'],
            'longitude': hotel_id_detail['hotel']['longitude'],
            'checkin': hotel_id_detail['offers'][0]['checkInDate'],
            'checkout': hotel_id_detail['offers'][0]['checkOutDate'],
            'boardType': boardType,
            'desc': hotel_id_detail['offers'][0]['room']['description']['text'],
            'price_base': hotel_id_detail['offers'][0]['price']['base'],
            'price_total': hotel_id_detail['offers'][0]['price']['total'],
            'price_currency': hotel_id_detail['offers'][0]['price']['currency'],
            'price_percentage': format(float(hotel_id_detail['offers'][0]['price']['total']) - float(hotel_id_detail['offers'][0]['price']['base']),f".{2}f"),
            'price_avg_base': hotel_id_detail['offers'][0]['price']['variations']['average']['base'],
            'policy': policy,
            'deposit':deposit,
            'username': request.user.username,
            'no_rooms': request.session.get('no_rooms'),
            'no_of_days': len(hotel_id_detail['offers'][0]['price']['variations']['changes']),
        }

        return render(request, 'booking/hotel_details.html', { 'offer':offer, 'user':request.user })

@login_required
def flight_detail(request):
    flight_data = request.session.get('flight-data')
    flight_data_list = json.loads(flight_data)
    
    if flight_data is None:
        return HttpResponse("Some error Occured! Try Again")
    else:
        flight_id = request.GET.get('flight_id')

        if flight_id is None:
            return HttpResponse("Hotel ID not being fetched!")
        
        for flight_detail in flight_data_list:
            if flight_id == flight_detail['id']:
                flight_id_detail = flight_detail
                break

        if len(flight_id_detail['itineraries'][0]['segments']) > 1:
            flight_type = 'Hopping'
        else:
            flight_type = 'Direct'

        try:
            meal_services = flight_id_detail['travelerPricings'][0]['fareDetailsBySegment'][0]['amenities'][2]['isChargeable']
        except KeyError:
            meal_services = 'N/A'

        try:
           flight_company = flight_id_detail['travelerPricings'][0]['fareDetailsBySegment'][0]['amenities'][1]['description']
        except KeyError:
            flight_company = None

        try:
           checked_baggage_weight= flight_id_detail['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weight']
        except KeyError:
            checked_baggage_weight = 'Unavailable'
        
        if flight_type == 'Direct':
            offer = {
                'flight_id':flight_id,
                'flight_type': 'Direct',
                'total_duration': flight_id_detail['itineraries'][0]['duration'],
                'carrierCode': flight_id_detail['itineraries'][0]['segments'][0]['carrierCode'],
                'departure_loc': flight_id_detail['itineraries'][0]['segments'][0]['departure']['iataCode'],
                'departure_time': flight_id_detail['itineraries'][0]['segments'][0]['departure']['at'],
                'arrival_loc': flight_id_detail['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                'arrival_time': flight_id_detail['itineraries'][0]['segments'][0]['arrival']['at'],
                'cabin_type': flight_id_detail['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'],
                'flight_company': flight_company,
                'meal_services': meal_services,
                'available_seats': flight_id_detail['numberOfBookableSeats'],
                'checked_baggage_weight': checked_baggage_weight,
                'price_per_person': flight_id_detail['travelerPricings'][0]['price']['total'],
                'price_currency': flight_id_detail['travelerPricings'][0]['price']['currency'],
                'price_total': flight_id_detail['price']['total'],
                'no_of_adults': len(flight_id_detail['travelerPricings']),
                'username': request.user,
            }
        else:
            offer = {
                'flight_id':flight_id,
                'flight_type': 'Hopping',
                'total_duration': flight_id_detail['itineraries'][0]['duration'],
                'carrierCode': flight_id_detail['itineraries'][0]['segments'][0]['carrierCode'],
                'departure_loc': flight_id_detail['itineraries'][0]['segments'][0]['departure']['iataCode'],
                'departure_time': flight_id_detail['itineraries'][0]['segments'][0]['departure']['at'],
                'hopping_loc': flight_id_detail['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                'hopping_at': flight_id_detail['itineraries'][0]['segments'][0]['arrival']['at'],
                'hopping_dt': flight_id_detail['itineraries'][0]['segments'][1]['departure']['at'],
                'arrival_loc': flight_id_detail['itineraries'][0]['segments'][1]['arrival']['iataCode'],
                'arrival_time': flight_id_detail['itineraries'][0]['segments'][1]['arrival']['at'],
                'hop_1_duration': flight_id_detail['itineraries'][0]['segments'][0]['duration'],
                'hop_2_duration': flight_id_detail['itineraries'][0]['segments'][1]['duration'],
                'price_total': flight_id_detail['price']['total'],
                'no_of_adults': len(flight_id_detail['travelerPricings']),
                'cabin_type': flight_id_detail['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'],
                'available_seats': flight_id_detail['numberOfBookableSeats'],
                'checked_baggage_weight': checked_baggage_weight,
                'price_per_person': flight_id_detail['travelerPricings'][0]['price']['total'],
                'price_currency': flight_id_detail['travelerPricings'][0]['price']['currency'],
                'username': request.user,
            }
        return render(request, 'booking/flight_details.html', { 'offer':offer, 'range_of_adults':range(offer['no_of_adults']), 'user':request.user })


@login_required
def confirm_booking(request):
    if request.method == 'POST':
        user = request.user
        if 'hotel-submit' in request.POST:
            hotel_price  = request.POST.get('hotel-price')
            hotel_name = request.POST.get('hotel-name')
            hotel_city = request.POST.get('hotel-city')
            no_rooms = request.POST.get('hotel-no-rooms')
            hotel_id = request.POST.get('hotel-id')
            check_in = request.POST.get('check-in')
            check_out = request.POST.get('check-out')
            currency = request.POST.get('currency')

            hotel_booking = Hotel_Booking.objects.create(
                user = user,
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                hotel_city=hotel_city,
                no_rooms=no_rooms,
                check_in=check_in,
                check_out=check_out,
                total_amount=hotel_price,
                amount_currency=currency,
                payment_status=False
            )

            hotel_booking.save()

            return redirect(reverse('payments:payment_page', kwargs={'booking_id':hotel_booking.booking_id,'booking_type':'hotel'}))

        elif 'flight-submit' in request.POST:
            flight_id = request.POST.get('flight-id')
            flight_carrierCode = request.POST.get('flight-carrierCode') 
            no_adults = request.POST.get('flight-no-adults')
            dep_time = request.POST.get('flight-dep-at')
            dep_loc = request.POST.get('flight-dep-loc')
            arr_time = request.POST.get('flight-arrival-at')
            arr_loc = request.POST.get('flight-arrival-loc')
            flight_price = request.POST.get('flight-price')
            currency = request.POST.get('currency')

            passenger_names = []
            for i in range(int(no_adults)):
                name = request.POST.get(f'name{i+1}')
                passenger_names.append(name)

            flight_booking = Flight_Booking.objects.create(
                user = user,
                flight_id = flight_id,
                flight_carrierCode = flight_carrierCode,
                no_adults = int(no_adults),
                departure_location = dep_loc,
                departure_time = dep_time[11:],
                departure_date = dep_time[0:10],
                arrival_location = arr_loc,
                arrival_time = arr_time[11:],
                arrival_date = arr_time[0:10],
                total_amount = flight_price,
                amount_currency = currency,
                payment_status = False
            )
            flight_booking.set_passenger_name(passenger_names)
            flight_booking.save()
        
            return redirect(reverse('payments:payment_page', kwargs={'booking_id':flight_booking.booking_id,'booking_type':'flight'}))
        
    return HttpResponse("<h1>Invalid Request 404</h1>")

