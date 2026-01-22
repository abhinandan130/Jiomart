from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def nocache(view_func):
    return cache_control(
        no_cache=True,
        no_store=True,
        must_revalidate=True,
        max_age=0
    )(view_func)


def session_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            messages.error(request, "Login required.")
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return wrapper