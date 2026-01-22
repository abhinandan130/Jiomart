from django.shortcuts import render
from django.http import JsonResponse
from .models import Product
from django.db.models import Q
from .models import Product

def product_list(request, category=None):
    user_location = None
    customer_id = request.session.get("user_id")

    if customer_id:
        from apps.accounts.models import Customer
        try:
            customer = Customer.objects.get(id=customer_id)
            user_location = customer.location
        except Customer.DoesNotExist:
            user_location = None

    active_category = category or "all"

    if category and category != "all":
        products = Product.objects.filter(category=category)

        sections = [{
            "title": category.capitalize() + " Deals",
            "category": category,
            "products": products,
        }]
    else:
        categories = Product.objects.values_list('category', flat=True).distinct()

        sections = []
        for cat in categories:
            products_in_cat = Product.objects.filter(category=cat)[:12]

            if products_in_cat.exists():
                sections.append({
                    "title": cat.capitalize() + " Deals",
                    "category": cat,
                    "products": products_in_cat,
                })

    context = {
        "active_category": active_category,
        "sections": sections,
        "user_location": user_location,
    }

    return render(request, "products/product_list.html", context)





def product_list_api(request):
    category = request.GET.get("category")

    qs = Product.objects.all()

    if category and category != "all":
        qs = qs.filter(category=category)

    data = []
    for p in qs:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "image": p.image.url if p.image else "",
        })

    return JsonResponse({"products": data})




def search_api(request):
    q = request.GET.get("q", "").strip()

    if not q or len(q) < 2:
        return JsonResponse({
            "suggestions": [],
            "products": [],
            "categories": [],
            "brands": []
        })

    products_qs = Product.objects.filter(
        Q(name__icontains=q) | Q(category__icontains=q),
        is_active=True
    )

    products = [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "image": p.image.url if p.image else "",
        "category": p.category
    } for p in products_qs[:6]]

    suggestions = list(
        products_qs.values_list("name", flat=True).distinct()[:6]
    )

    categories = list(
        Product.objects.values_list("category", flat=True).distinct()
    )

    brands = set()
    for p in products_qs:
        brand = p.name.split(" ")[0]
        brands.add(brand)

    return JsonResponse({
        "suggestions": suggestions,
        "products": products,
        "categories": categories,
        "brands": list(brands)
    })



def products_by_category(request, category):
    products = Product.objects.filter(category__iexact=category, is_active=True)
    return render(request, "products/product_list.html", {
        "products": products,
        "selected_category": category
    })


def products_by_brand(request, brand):
    products = Product.objects.filter(
        name__istartswith=brand,
        is_active=True
    )
    return render(request, "products/product_list.html", {
        "products": products,
        "selected_brand": brand
    })
