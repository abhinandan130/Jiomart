from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "name", "location", "otp", "otp_created_at", "is_registered", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
