from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User


def athenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(
                request,
                "You are already logged in as @{0}".format(request.user.username),
            )
            return redirect("my_account")

        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            user_id = (
                kwargs.get("user_id", None)
                if kwargs.get("user_id", None)
                else request.user.id
            )
            user = get_object_or_404(User, pk=user_id)
            if user.groups.exists():
                groups = user.groups.all()

            if [group for group in groups if group.name in allowed_roles]:
                return view_func(request, *args, **kwargs)
            else:
                messages.info(
                    request,
                    "You are not authorized to view this page",
                )
                raise PermissionDenied("You Are Not Authorized to view this page")

        return wrapper_func

    return decorator


def only_admin(view_func):
    def wrapper_func(request, *args, **kwargs):
        print(request.user.is_superuser, request.user)
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.info(
                request,
                "You are not authorized to view this page",
            )
            raise PermissionDenied("You are not authorized to view this page")

    return wrapper_func


def athurized_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(
                "admin_dashboard:dashboard",
                user_id=request.user.id,
            )
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
