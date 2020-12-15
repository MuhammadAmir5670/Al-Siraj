from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


from .tokens import account_activation_token
from .decorators import *
from .forms import SignUpForm, StudentForm

# Create your views here.

from main.models import add_user_to_group, remove_user_from_group


@athenticated_user
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        next_ = request.GET.get("next")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if next_:
                return redirect(next_)
            else:
                return redirect("dashboard:dashboard", user_id=user.id)
        else:
            messages.warning(
                request,
                "Please enter a correct username and password. And make sure you have comfirm your registration via email sent.",
            )

    context = {}
    return render(request, "accounts/log_in.html", context)


@athenticated_user
def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = "Activate Your AL-Siraj Account"
            message = render_to_string(
                "accounts/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject, message)
            return render(request, "accounts/account_activation_sent.html", {})
    else:
        form = SignUpForm()
    context = {"form": form}
    return render(request, "accounts/sign_up.html", context)


def resend_activation_token(request):
    if request.method == "POST":
        user_email = request.POST["user_email"]
        user = User.objects.filter(email=user_email)[0]
        if user is not None:
            current_site = get_current_site(request)
            subject = "Activate Your AL-Siraj Account"
            message = render_to_string(
                "accounts/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject, message)
            return render(request, "accounts/account_activation_sent.html", {})
        else:
            message.info(
                "Sorry, but the given email address is not recognized. make sure you have typed it correctly."
            )
            return render(request, "accounts/resend_activation_mail.html", {})
    else:
        return render(request, "accounts/resend_activation_mail.html", {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.student.email_confirmed = True
        user.save()
        # adding user to the student group
        add_user_to_group(group_id=1, user_id=user.id)

        # login the user
        login(request, user)
        return redirect("dashboard:courses")
    else:
        return render(request, "accounts/account_activation_invalid.html")


class UserAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    login_url = "/accounts/login/"
    fields = ("first_name", "last_name", "username", "email")
    template_name = "accounts/my_account.html"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:dashboard", kwargs={"user_id": self.request.user.id}
        )

    def get_object(self):
        return self.request.user
