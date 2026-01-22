from django.contrib import admin
from .models import Order, OrderItem, Address


# -------------------------
# Order Items Inline
# -------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal")


# -------------------------
# Order Admin
# -------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "total_amount",
        "payment_status",
        "status",
        "created_at",
    )

    list_editable = ("payment_status", "status",)
    list_filter = ("payment_status", "status", "created_at")
    search_fields = ("order_number", "customer__email")
    list_display_links = ("order_number",)

    readonly_fields = (
        "order_number",
        "customer",
        "address",
        "total_amount",
        "created_at",
    )

    inlines = [OrderItemInline]

    # -------------------------
    # ADMIN ACTIONS
    # -------------------------
    actions = [
        "accept_order",
        "mark_shipped",
        "mark_delivered",
        "cancel_order",
    ]

    def accept_order(self, request, queryset):
        queryset.update(status="pending")
    accept_order.short_description = "Accept selected orders"

    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")
    mark_shipped.short_description = "Mark selected orders as Shipped"

    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")
    mark_delivered.short_description = "Mark selected orders as Delivered"

    def cancel_order(self, request, queryset):
        queryset.update(status="cancelled")
    cancel_order.short_description = "Cancel selected orders"


# -------------------------
# Address Admin
# -------------------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "state", "pincode", "created_at")
    search_fields = ("full_name", "city", "state")
