from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("customer", "created_at")
    list_filter = ("customer", "created_at")
    search_fields = ("customer",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    list_filter = ("cart", "product")
    search_fields = ("cart",)