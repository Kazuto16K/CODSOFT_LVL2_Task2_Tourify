from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.base, name='base'),
    path('login/',views.user_login, name='login'),
    path('register/',views.sign_up, name='register'),
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'),name='password_reset'),
    path('password_reset/done',auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done',auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),
    
]
