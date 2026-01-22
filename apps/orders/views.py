from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import razorpay

from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem, Address
from apps.accounts.models import Customer


# -------------------------------
# Helper
# -------------------------------
def _get_logged_in_customer(request):
    customer_id = request.session.get("user_id")
    if not customer_id:
        return None
    return Customer.objects.filter(id=customer_id).first()


# -------------------------------
# CREATE ORDER (Razorpay)
# -------------------------------
@csrf_exempt
def create_order(request):
    customer = _get_logged_in_customer(request)
    if not customer:
        return JsonResponse({"error": "Login required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Safe JSON parsing
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid or empty JSON body"},
            status=400
        )

    address_id = data.get("address_id")
    if not address_id:
        return JsonResponse({"error": "Address required"}, status=400)

    address = get_object_or_404(Address, id=address_id, customer=customer)

    cart = Cart.objects.filter(customer=customer).first()
    if not cart or not cart.items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)

    cart_items = cart.items.select_related("product")

    total_amount = sum(
        item.product.price * item.quantity for item in cart_items
    )

    # ✅ Razorpay expects integer paise
    amount_in_paise = int(total_amount * 100)

    # ✅ Create Razorpay client (1.4.2 safe)
    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    try:
        with transaction.atomic():
            # Create DB Order
            order = Order.objects.create(
                customer=customer,
                address=address,
                total_amount=total_amount,
                payment_status="pending",
                status="pending",
            )

            # Create Order Items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    subtotal=item.product.price * item.quantity,
                )

            # ✅ Create Razorpay Order (IMPORTANT FIXES HERE)
            razorpay_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"order_{order.id}",  # ✅ REQUIRED FOR STABILITY
                "payment_capture": 1
            })

            order.razorpay_order_id = razorpay_order["id"]
            order.save()

    except Exception as e:
        return JsonResponse(
            {"error": "Order creation failed", "details": str(e)},
            status=500
        )

    return JsonResponse({
        "razorpay_order_id": razorpay_order["id"],  # 🔥 REQUIRED
        "order_number": order.order_number,         # 🔥 REQUIRED
        "amount": razorpay_order["amount"],
        "currency": razorpay_order["currency"],
        "key": settings.RAZORPAY_KEY_ID
    })



# -------------------------------
# ADDRESS VIEWS
# -------------------------------
def select_address(request):
    customer = _get_logged_in_customer(request)
    if not customer:
        return redirect("accounts:login")

    addresses = Address.objects.filter(customer=customer)
    return render(request, "orders/select_address.html", {
        "addresses": addresses
    })


def add_address(request):
    customer = _get_logged_in_customer(request)
    if not customer:
        return redirect("accounts:login")

    if request.method == "POST":
        Address.objects.create(
            customer=customer,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line=request.POST.get("address_line"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
        )

        messages.success(request, "Address added successfully")
        return redirect("orders:select_address")

    return render(request, "orders/add_address.html")


# -------------------------------
# MY ORDERS
# -------------------------------
def my_orders(request):
    customer = _get_logged_in_customer(request)
    if not customer:
        return redirect("accounts:login")

    orders = Order.objects.filter(customer=customer).order_by("-created_at")
    return render(request, "orders/my_orders.html", {
        "orders": orders
    })


def order_detail(request, order_number):
    customer = _get_logged_in_customer(request)
    if not customer:
        return redirect("accounts:login")

    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer=customer
    )
    return render(request, "orders/order_detail.html", {
        "order": order
    })


# -------------------------------
# PAYMENT SUCCESS (Razorpay)
# -------------------------------
@csrf_exempt
def payment_success(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse(
            {"error": "Missing payment details"},
            status=400
        )

    try:
        order = Order.objects.get(
            razorpay_order_id=razorpay_order_id
        )
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    # Verify signature
    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse(
            {"error": "Signature verification failed"},
            status=400
        )

    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature
    order.payment_status = "paid"
    order.status = "confirmed"
    order.save()
    
    cart = Cart.objects.filter(customer=order.customer).first()
    if cart:
        cart.items.all().delete()

    return JsonResponse({
        "status": "success",
        "order_number": order.order_number
    })
