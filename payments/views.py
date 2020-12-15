from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .models import Transaction
from accounts.decorators import allowed_users, only_admin
from main.models import Course, Enrollment
from main.models import add_user_to_group, remove_user_from_group
from .transaction import (
    PostData,
    validate_data,
    extract_transaction_data,
    create_transaction,
    check_payment_status,
)


# Create your views here.


@login_required
@allowed_users(allowed_roles=["students"])
def checkout(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        payment_method = request.POST["Payment_method"]
        return redirect(
            "payments:checkout_redirect", course_id=course_id, T_method=payment_method
        )
    context = {"course": course}
    return render(request, "payments/checkout.html", context=context)


@login_required
@allowed_users(allowed_roles=["students"])
def checkout_redirect(request, course_id, T_method):
    course = get_object_or_404(Course, pk=course_id)
    if course is not None:
        jazzcash_post_data = PostData(course, request.user, T_method)
        jazzcash_post_data.set_return_url(course, request.user)
    context = {
        "post_data": jazzcash_post_data.data,
        "post_url": jazzcash_post_data.JAZZCASH_HTTP_POST_URL,
    }
    return render(request, "payments/checkout_redirect.html", context=context)


@csrf_exempt
@allowed_users(allowed_roles=["students"])
def payment_confirm(request, course_id, user_id):
    # Getting the user and course data
    course = get_object_or_404(Course, pk=course_id)
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        # fetching data if request method is POST
        data = extract_transaction_data(request)
        if validate_data(data, course.to_PKR()) and check_payment_status(
            data["ResponseCode"]
        ):
            # Store Enrollment and Transaction For User If
            # Data is valid
            enrollment = Enrollment.objects.create(user=user, course=course)
            transaction = create_transaction(data, enrollment)
            # redirecting the user the Payment Status Page
            return redirect(
                "payments:payment_status",
                enrollment_id=enrollment.id,
                transaction_id=transaction.id,
            )
        else:
            # Sending Warning Messages to the View if data is invalid
            messages.warning(
                request,
                "Some Serious error occurs please check transaction logs for more detail. Response Message: {} Response Code: {}".format(
                    data["ResponseMessage"], data["ResponseCode"]
                ),
            )
            return redirect("payments:payment_message")
    else:
        raise PermissionDenied("invalid request....")


def payment_message(request):
    return render(request, "payments/payment_confirm.html", context={})


@login_required
@allowed_users(allowed_roles=["students"])
def payment_status(request, enrollment_id, transaction_id):
    enrollment = Enrollment.get_enrollment(
        Enrollment, user_id=request.user.id, enrollment_id=enrollment_id
    )
    transaction = Transaction.get_transaction(
        Transaction, transaction_id=transaction_id, enrollment_id=enrollment.id
    )
    if transaction.status:
        enrollment.active = True
        enrollment.save()
        # sending course enrollment confirmation message to the user
        message = render_to_string(
            "payments/payment_email.html",
            {
                "enrollment": enrollment,
                "transaction": transaction,
            },
        )
        request.user.email_user("AL-Siraj Course Confirmation", message)
        # adding user to the enrolled_student group
        add_user_to_group(group_id=2, user_id=request.user.id)

        context = {"transaction": transaction}
        return render(request, "payments/payment_status.html", context=context)
    else:
        enrollment.delete()
        transaction.delete()
        messages.warning(request, "Payment Failed")
        return render(request, "payments/payment_status.html", {})
    raise Http404("Invalid Request")


# JAZZCASH PAGE REDIRECTION TEST PAGE VIEW
@login_required
@only_admin
def test_checkout(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course is not None:
        jazzcash_post_data = PostData(course, request.user)
    context = {
        "post_data": jazzcash_post_data.data,
        "post_url": jazzcash_post_data.JAZZCASH_HTTP_POST_URL,
    }
    return render(request, "payments/test_checkout.html", context=context)


# JAZZCASH PAGE REDIRECTION TEST PAGE VIEW
@login_required
@only_admin
def test_checkout_confirmation(request):
    return render(request, "payments/test_confirmation.html", context={})
