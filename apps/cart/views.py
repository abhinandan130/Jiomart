from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem
from apps.products.models import Product
from accounts.decorators import nocache


# =====================================
# ADD TO CART (HOME + BUY NOW)
# =====================================
@nocache
@require_POST
def add_to_cart(request, product_id):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )

    mode = request.POST.get("mode")  # normal | buy_now

    cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()

    response = {
        "success": True,
        "already_exists": not created,
    }

    if mode == "buy_now":
        response["redirect_url"] = "/cart/"

    return JsonResponse(response)

# =====================================
# CART COUNT (NAVBAR)
# =====================================
@nocache
def cart_count(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return JsonResponse({"count": 0})

    try:
        cart = Cart.objects.get(customer_id=customer_id)
        count = sum(item.quantity for item in cart.items.all())
    except Cart.DoesNotExist:
        count = 0

    return JsonResponse({"count": count})


# =====================================
# CART PAGE
# =====================================
@nocache
def cart_page(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return render(request, "cart/cart.html", {
            "items": [],
            "total": 0
        })

    cart = Cart.objects.filter(customer_id=customer_id).first()

    items = []
    total = 0

    if cart:
        for item in cart.items.select_related("product"):
            subtotal = item.quantity * item.product.price
            total += subtotal

            items.append({
                "id": item.id,  # REQUIRED for JS
                "name": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "image": item.product.image.url if item.product.image else ""
            })

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total,
        "hide_footer": True
    })


# =====================================
# UPDATE QUANTITY (+ / -)
# =====================================
@nocache
@require_POST
def update_cart_quantity(request):
    item_id = request.POST.get("item_id")
    action = request.POST.get("action")

    item = get_object_or_404(CartItem, id=item_id)
    cart = item.cart
    deleted = False

    if action == "increase":
        item.quantity += 1
        item.save()

    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
            deleted = True

    cart_total = sum(i.quantity * i.product.price for i in cart.items.all())
    cart_count = sum(i.quantity for i in cart.items.all())

    return JsonResponse({
        "success": True,
        "deleted": deleted,
        "quantity": 0 if deleted else item.quantity,
        "item_subtotal": 0 if deleted else item.quantity * item.product.price,
        "cart_total": cart_total,
        "cart_items_count": cart_count
    })
