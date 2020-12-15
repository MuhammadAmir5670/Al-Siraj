from django.db import models
from django.shortcuts import Http404

from main.models import Enrollment

# Create your models here.


class Transaction(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=70)
    transaction_retreival_reference_no = models.CharField(max_length=200, null=True)
    total_amount = models.IntegerField()
    paid_amount = models.IntegerField()
    status = models.BooleanField(default=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, null=True)

    def get_transaction(self, transaction_id, enrollment_id):
        transaction = self.objects.filter(
            id=transaction_id, enrollment__id=enrollment_id
        )
        if transaction:
            return transaction[0]
        else:
            raise Http404("Page Not Found")
