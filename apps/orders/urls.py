from django.urls import path
from .views import create_order, order_success, download_invoice

urlpatterns = [
    path("create/", create_order, name="create_order"),
    path("success/<str:order_number>/", order_success, name="order_success"),
    path("invoice/<str:order_number>/", download_invoice, name="download_invoice"),
]
