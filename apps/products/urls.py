from django.urls import path
from .views import product_list, product_list_api, search_api, products_by_category, products_by_brand

urlpatterns = [
    path("", product_list, name="product_list"),  # Everything Store (HOME)
    path("category/<str:category>/", product_list, name="product_by_category"),

    path("api/products/", product_list_api, name="product_list_api"),
    path("api/search/", search_api, name="search-api"),

    path("category/<str:category>/", products_by_category, name="products_by_category"),
    path("brand/<str:brand>/", products_by_brand, name="products_by_brand"),


]
