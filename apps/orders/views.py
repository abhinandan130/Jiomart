from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from django.db import transaction

from .utils.invoice import generate_invoice_pdf
from apps.cart.models import Cart, CartItem
from .models import Order, OrderItem
from apps.accounts.models import Customer


@require_POST
@transaction.atomic
def create_order(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        messages.error(request, "Login required to place order.")
        return redirect("login")

    cart = Cart.objects.filter(customer_id=customer_id).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart_page")

    total_amount = Decimal("0.00")

    # 🔒 STEP 1: Stock validation
    for item in cart.items.select_related("product"):
        if item.product.stock < item.quantity:
            messages.error(
                request,
                f"Insufficient stock for {item.product.name}"
            )
            return redirect("cart_page")

        total_amount += item.quantity * item.product.price

    # 🔒 STEP 2: Create order
    order = Order.objects.create(
        customer_id=customer_id,
        total_amount=total_amount,
        status="pending"
    )

    # 🔒 STEP 3: Create order items + decrement stock
    for item in cart.items.select_related("product"):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            subtotal=item.quantity * item.product.price
        )

        # 🔥 DECREMENT PRODUCT STOCK
        item.product.stock -= item.quantity
        item.product.save(update_fields=["stock"])

    # 🔒 STEP 4: Clear cart
    cart.items.all().delete()

    return redirect("order_success", order_number=order.order_number)


def order_success(request, order_number):
    customer_id = request.session.get("user_id")

    order = Order.objects.filter(
        order_number=order_number,
        customer_id=customer_id
    ).prefetch_related("items__product").first()

    if not order:
        return redirect("product_list")

    return render(request, "orders/order_success.html", {
        "order": order
    })


def download_invoice(request, order_number):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return HttpResponseForbidden("Login required")

    order = get_object_or_404(
        Order,
        order_number=order_number,
        customer_id=customer_id
    )

    return generate_invoice_pdf(order)
