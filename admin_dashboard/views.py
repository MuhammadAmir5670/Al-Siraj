from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import send_mail
from online_learning_system.settings import EMAIL_HOST_USER

# Create your views here.
from main.models import (
    get_data_for_admin,
    get_students,
    Trial,
    get_user_enrollment_count,
)
from accounts.decorators import only_admin


@login_required
@only_admin
def admin_dashboard(request, user_id):
    context = get_data_for_admin()
    return render(request, "admin_dashboard/admin_dashboard.html", context=context)


@login_required
@only_admin
def students(request, user_id):
    students = User.objects.all().exclude(groups__id=4)
    enrollments_count = get_user_enrollment_count()
    students = zip(students, enrollments_count)
    context = {"students": students}
    return render(request, "admin_dashboard/all_students.html", context=context)


@login_required
@only_admin
def enrolled(request, user_id):
    students = get_students(_type="active")
    context = {
        "students": students,
    }
    return render(request, "admin_dashboard/enrolled.html", context=context)


@login_required
@only_admin
def unenrolled(request, user_id):
    students = get_students(_type="inactive")
    context = {
        "students": students,
    }
    return render(request, "admin_dashboard/unenrolled.html", context=context)


@login_required
@only_admin
def all_trials(request, user_id):
    trials = Trial.get_trials(Trial).exclude(status=True)
    context = {
        "trials": trials,
    }
    return render(request, "admin_dashboard/all_trials.html", context=context)


@login_required
@only_admin
def active_trials(request, user_id):
    trials = Trial.get_active_trialies(Trial).exclude(status=True)
    context = {
        "trials": trials,
    }
    return render(request, "admin_dashboard/active_trials.html", context=context)


@login_required
@only_admin
def deactive_trials(request, user_id):
    trials = Trial.get_inactive_trialies(Trial).exclude(status=True)
    context = {
        "trials": trials,
    }
    return render(request, "admin_dashboard/deactive_trials.html", context=context)


@login_required
@only_admin
def send_meeting(request, user_id, s_id, course_name):
    user = get_object_or_404(User, pk=s_id)
    if request.method == "POST":
        meeting_link = request.POST["meeting_link"]
        subject = "Al_Siraj Class Meeting"
        message = render_to_string(
            "admin_dashboard/meeting_email.html",
            {
                "meeting_id": meeting_link,
                "course": course_name,
                "admin": "Hafiz Nabeel",
            },
        )
        user.email_user(subject, message)
        messages.success(request, "Meeting has been sent Successfully")
        return redirect(request.build_absolute_uri())

    context = {
        "user": user,
    }
    return render(request, "admin_dashboard/send_meeting.html", context=context)


@login_required
@only_admin
def send_mail_to(request, to=0):
    if request.method == "POST":
        if to == 0:
            users = User.objects.filter(groups__name="students")
        elif to == 1:
            users = [enrollment.user for enrollment in get_students(_type="active")]
        elif to == 2:
            users = [enrollment.user for enrollment in get_students(_type="inactive")]
        elif to == 3:
            users = [trial.user for trial in Trial.get_trials(Trial)]
        else:
            raise Http404("Invalid Request")
        # sending Mails
        subject = request.POST["subject"]
        message = request.POST["message"]
        receivers = [user.email for user in users]
        status = send_mail(
            subject,
            message,
            from_email=EMAIL_HOST_USER,
            recipient_list=receivers,
        )
        if status != 0:
            messages.info(
                request, "Mails Has been successfully sent to the All Students."
            )
        else:
            messages.info(request, "Unable to send Mails.")
        return redirect("admin_dashboard:dashboard", user_id=request.user.id)
    else:
        context = {}
        return render(
            request, "admin_dashboard/send_mail_to_users.html", context=context
        )
