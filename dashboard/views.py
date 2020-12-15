from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail

from accounts.decorators import *
from main.models import Course, Enrollment
from main.models import add_user_to_group, remove_user_from_group, get_data_for_admin

# Create your views here.


@login_required
@athurized_only
def dashboard(
    request,
    user_id,
):
    user = get_object_or_404(User, pk=user_id)
    enrollments = Enrollment.user_enrollments(Enrollment, user.id)
    context = {"enrollments": enrollments}
    return render(request, "dashboard/dashboard.html", context=context)


@login_required
@allowed_users(allowed_roles=["students"])
def courses(request):
    return render(request, "dashboard/courses.html", context={})


@login_required
@allowed_users(allowed_roles=["students"])
def courses_data(request, course_id):
    courses, name = Course.get_course(Course, course_id)
    if not courses:
        raise Http404("invalid request")
    else:
        courses = Course.seperate_query_sets(Course, courses)
        context = {"name": name, "courses": courses}
        return render(request, "dashboard/courses_data.html", context=context)


@login_required
@allowed_users(allowed_roles=["students"])
def take_trial(request):
    return render(request, "dashboard/take_trial.html", context={})


@login_required
@allowed_users(allowed_roles=["students"])
def confirm_trial(request, course_id):
    course, course_name = Course.get_course(Course, course_id=course_id)
    if request.method == "POST":
        trial = request.user.trial
        if trial.trial_available():
            # ADDING USER TO THE TRIAL GROUP
            trial.status = False
            trial.course = course_name
            trial.set_trial_datetime()
            trial.save()

            add_user_to_group(group_id=3, user_id=request.user.id)
            messages.success(request, "You are Successfully enrolled in the trial.")
            return redirect(
                "dashboard:dashboard",
                user_id=request.user.id,
            )
        else:
            messages.warning(
                request,
                "you are not elligible for this trial. may be becuase you have already taken one.",
            )
            return redirect("dashboard:dashboard", user_id=request.user.id)
    else:
        context = {
            "course": course,
        }
        return render(request, "dashboard/confirm_trial.html", context=context)


@login_required
@allowed_users(allowed_roles=["students"])
def contact(request):
    enrollments = Enrollment.user_enrollments(Enrollment, request.user.id)
    if enrollments:
        if request.method == "POST":
            f_name = request.POST["f_name"]
            l_name = request.POST["l_name"]
            user_email = request.user.email
            user_message = request.POST["user_message"]
            message = render_to_string(
                "dashboard/contact_email.html",
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
                from_email=user_email,
                recipient_list=["al.siraj5670@gmail.com"],
            )
            if status != 0:
                messages.success(
                    request, "Your Message Has been successfully sent to the Admin"
                )
            else:
                messages.warning(request, "Unable to send message")
            return redirect("dashboard:dashboard", user_id=request.user.id)
        else:
            return render(request, "dashboard/contact.html", context={})
    else:
        messages.warning(
            request,
            "you cannot request for meeting arrangement. your are not enrolled in any course. please get enrolled in any course first then you can use this option.",
        )
        return redirect("dashboard:courses")
