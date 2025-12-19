from django.urls import path
from . import views

urlpatterns = [
    path("api/cart/add/<int:product_id>/", views.add_to_cart),
    path("api/cart/count/", views.cart_count),
    path("cart/", views.cart_page, name="cart_page"),
    path("api/cart/update/<int:item_id>/", views.update_cart_quantity),
    path("api/cart/update-qty/", views.update_cart_quantity, name="update_cart_quantity"),
    # path("api/cart/buy-now/<int:product_id>/", views.buy_now, name="buy_now"),


]
