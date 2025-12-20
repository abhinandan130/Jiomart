from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('verify-otp/', views.verify_otp, name="verify_otp"),
    path('register-details/', views.register_details, name="register_details"),
    path('resend-otp/', views.resend_otp, name="resend_otp"),
    path('profile/', views.profile_view, name="profile"),
    path('logout/', views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
]
