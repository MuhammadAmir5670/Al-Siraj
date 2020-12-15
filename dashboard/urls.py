from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("<int:user_id>/", views.dashboard, name="dashboard"),
    path(
        "courses/",
        views.courses,
        name="courses",
    ),
    path("courses/<int:course_id>/", views.courses_data, name="courses_data"),
    path("take_trial/", views.take_trial, name="take_trial"),
    path("trial_confirm/<int:course_id>", views.confirm_trial, name="trial_confirm"),
    path("contact/", views.contact, name="contact"),
]
