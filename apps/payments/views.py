from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.shortcuts import render, get_object_or_404
from apps.orders.models import Order
from apps.cart.models import Cart
from .models import Payment
from .razorpay_client import client

def razorpay_checkout(request):
    address_id = request.GET.get("address_id")
    if not address_id:
        return redirect("cart:cart")

    return render(request, "payments/razorpay_checkout.html", {
        "address_id": address_id
    })


@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    order_number = data.get("order_number")
    razorpay_payment_id = data.get("razorpay_payment_id")

    if not order_number:
        return JsonResponse({"error": "Order number missing"}, status=400)

    order = Order.objects.get(order_number=order_number)

    # ✅ UPDATE ORDER
    order.payment_status = "paid"
    order.status = "shipped"
    order.save()

    # ✅ CLEAR CART
    cart = Cart.objects.filter(customer=order.customer).first()
    if cart:
        cart.items.all().delete()
        cart.delete()

    return JsonResponse({
        "status": "success",
        "redirect_url": f"/payments/success/{order.order_number}/"
    })



def payment_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "payments/success.html", {
        "order": order
    })