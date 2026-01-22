from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # 🔹 Cart → Create Order (POST only)
    path("create/", views.create_order, name="create_order"),

    # 🔹 Address management
    path("add-address/", views.add_address, name="add_address"),

    # 🔹 Orders listing (My Orders page)
    path("", views.my_orders, name="my_orders"),

    # 🔹 Order details (AFTER payment success)
    path("<str:order_number>/", views.order_detail, name="order_detail"),

    # 🔹 Order success page (used after payment confirmation)
    path("payment-success/", views.payment_success, name="payment_success"),

]
