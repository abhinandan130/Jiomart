from django.urls import path
from .views import razorpay_checkout, verify_payment, payment_success

app_name = "payments"

urlpatterns = [
    path("checkout/", razorpay_checkout, name="razorpay_checkout"),
    path("verify/", verify_payment, name="verify_payment"),
    path("success/<str:order_number>/", payment_success, name="payment_success"),
]
