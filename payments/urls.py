from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/<str:booking_type>/<uuid:booking_id>/', views.payment_page, name='payment_page'),
    path('process_payment/<uuid:booking_id>/', views.process_payment, name='process_payment'),
    path('execute/', views.execute_payment, name='execute_payment'),
    path('cancel/', views.cancel_payment, name='cancel_payment'),
]