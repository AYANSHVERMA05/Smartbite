from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to continue.")
            return redirect('accounts:login')
        if not (request.user.is_customer or request.user.is_superuser):
            messages.error(request, "This page is reserved for customers.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def restaurant_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with a restaurant owner account.")
            return redirect('accounts:login')
        if not (request.user.is_restaurant_owner or request.user.is_superuser):
            messages.error(request, "Access restricted to Restaurant Owners.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in as an administrator.")
            return redirect('accounts:login')
        if not (request.user.is_admin_user or request.user.is_superuser or request.user.is_staff):
            messages.error(request, "Access restricted to System Administrators.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

