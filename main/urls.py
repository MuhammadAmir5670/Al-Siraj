from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("courses/<int:course_id>", views.courses, name="courses"),
    path(
        "course/quran_with_tajweed/<int:course_id>",
        views.quran_with_tajweed,
        name="quran_with_tajweed",
    ),
    path(
        "course/islam_for_kids/<int:course_id>",
        views.islam_for_kids,
        name="islam_for_kids",
    ),
    path(
        "course/noorani_qauida/<int:course_id>",
        views.noorani_qauida,
        name="noorani_qauida",
    ),
    path("contact/", views.contact, name="contact"),
    path("test_error_404/", views.test_error_404, name="error_404"),
    path("test_error_403/", views.test_error_403, name="error_403"),
    path("test_error_400/", views.test_error_400, name="error_400"),
    path("test_error_500/", views.test_error_500, name="error_500"),
]
