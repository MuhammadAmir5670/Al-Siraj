from django.urls import path

from . import views

app_name = "admin_dashboard"
urlpatterns = [
    path(
        "<int:user_id>/",
        views.admin_dashboard,
        name="dashboard",
    ),
    path(
        "<int:user_id>/students/",
        views.students,
        name="all",
    ),
    path(
        "<int:user_id>/students/enrolled",
        views.enrolled,
        name="enrolled",
    ),
    path(
        "<int:user_id>/students/unenrolled",
        views.unenrolled,
        name="unenrolled",
    ),
    path(
        "<int:user_id>/students/on_trial/",
        views.all_trials,
        name="all_trials",
    ),
    path(
        "<int:user_id>/students/active_trials/",
        views.active_trials,
        name="active_trials",
    ),
    path(
        "<int:user_id>/students/deactive_trials/",
        views.deactive_trials,
        name="deactive_trials",
    ),
    path(
        "<int:user_id>/students/send_meeting/<int:s_id>/<str:course_name>",
        views.send_meeting,
        name="send_meeting",
    ),
    path(
        "students/send_mail_to/<int:to>/",
        views.send_mail_to,
        name="send_mail_to",
    ),
]
