from django.urls import path,include
from users.views import user_logout
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('logout/',user_logout, name='logout'),
    path('home/',views.home,name="home"),
    path('password_change/',auth_views.PasswordChangeView.as_view(template_name='booking/password_change_form.html'), name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(template_name="booking/password_change_done.html"), name="password_change_done"),
    path('flight_search/',views.flight_search, name='flight_search'),
    path('hotel_search/',views.hotel_search, name='hotel_search'),
    path('flight_detail/',views.flight_detail, name='flight_detail'),
    path('hotel_detail/',views.hotel_detail, name='hotel_detail'),
    path('confirm_booking/',views.confirm_booking,name="confirm_booking"),
    path('profile/<str:username>',views.get_profile, name="get_profile"),
    path('get_pdf/',views.get_pdf, name="get_pdf"),

]