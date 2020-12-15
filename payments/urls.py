from django.urls import path

from . import views

app_name = "payments"
urlpatterns = [
    path("checkout/<int:course_id>", views.checkout, name="checkout"),
    path(
        "checkout/<int:course_id>/redirect/<str:T_method>/",
        views.checkout_redirect,
        name="checkout_redirect",
    ),
    path(
        "api/test_checkout/<int:course_id>",
        views.test_checkout,
        name="checkout_testing",
    ),
    path(
        "api/test_checkout/confirmation",
        views.test_checkout_confirmation,
        name="checkout_testing",
    ),
    path(
        "payment_confirm/<int:course_id>/<int:user_id>",
        views.payment_confirm,
        name="payment_confirm",
    ),
    path(
        "payment/status/<int:enrollment_id>/<int:transaction_id>",
        views.payment_status,
        name="payment_status",
    ),
    path(
        "payment/message/",
        views.payment_message,
        name="payment_message",
    ),
]
