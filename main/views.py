from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from online_learning_system.settings import EMAIL_HOST_USER

from .models import Course

# Create your views here.


def index(request):
    return render(request, "main/index.html", context={})


def about(request):
    return render(request, "main/about.html", context={})


def courses(request):
    return render(request, "main/courses.html", context={})


def quran_with_tajweed(request, course_id):
    if course_id != 1:
        print("error occurred")
        raise Http404("Page Not Found")
    context = {}
    return render(request, "main/quran_with_tajweed.html", context=context)


def islam_for_kids(request, course_id):
    if course_id != 2:
        raise Http404("Page Not Found")
    context = {}
    return render(request, "main/islam_for_kids.html", context=context)


def noorani_qauida(request, course_id):
    if course_id != 3:
        raise Http404("Page Not Found")
    context = {}
    return render(request, "main/noorani_qauida.html", context=context)


def contact(request):
    if request.method == "POST":
        f_name = request.POST["f_name"]
        l_name = request.POST["l_name"]
        user_email = request.POST["user_email"]
        user_message = request.POST["user_message"]
        print("Post Method Occurred")
        message = render_to_string(
            "main/contact_email.html",
            {
                "f_name": f_name,
                "l_name": l_name,
                "email": user_email,
                "message": user_message,
            },
        )
        status = send_mail(
            "A-Siraj Help Center",
            message,
            from_email=EMAIL_HOST_USER,
            recipient_list=["nabeelrana892gmail.com"],
        )
        if status != 0:
            messages.info("Your Message Has been successfully sent to the Admin")
        else:
            messages.info("Unable to send message")
        return redirect("main:contact")

    else:
        id = request.GET.get("id")
        if id:
            course = get_object_or_404(Course, pk=id)
            context = {"course": course}
        else:
            context = {}
        return render(request, "main/contact.html", context=context)


def courses(request, course_id):
    courses, name = Course.get_course(Course, course_id)
    if not courses:
        raise Http404("invalid request")
    else:
        courses = Course.seperate_query_sets(Course, courses)
        context = {"name": name, "courses": courses}
        return render(request, "main/courses.html", context=context)


# TESTING ERROR ERROR VIEWS
def test_error_404(request):
    context = {}
    return render(request, "main/404.html", context)


def test_error_403(request):
    context = {}
    return render(request, "main/403.html", context)


def test_error_400(request):
    context = {}
    return render(request, "main/400.html", context)


def test_error_500(request):
    context = {}
    return render(request, "main/500.html", context)


# ERROR VIEWS
def error_404(request, exception):
    context = {}
    return render(request, "main/404.html", context)


def error_403(request, exception):
    context = {}
    return render(request, "main/403.html", context)


def error_400(request, exception):
    context = {}
    return render(request, "main/400.html", context)


def error_500(request):
    context = {}
    return render(request, "main/500.html", context)
