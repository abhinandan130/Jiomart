from django.shortcuts import render
from django.http import JsonResponse
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {
        "products": products
    })


def product_list_api(request):
    """
    Returns products as JSON for JS.
    """
    products = Product.objects.filter(is_active=True)

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "category": p.category,
            "image": p.image.url if p.image else "",
        })

    return JsonResponse({"products": data})
