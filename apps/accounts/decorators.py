from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator

def nocache(view_func):
    return cache_control(
        no_cache=True,
        no_store=True,
        must_revalidate=True,
        max_age=0
    )(view_func)