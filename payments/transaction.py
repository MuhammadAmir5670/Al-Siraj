from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import hashlib
import hmac
from .models import Transaction


class PostData:
    # jazzcash configuration
    JAZZCASH_MERCHANT_ID = "MC13210"
    JAZZCASH_PASSWORD = "37w0z3ggte"
    JAZZCASH_INTEGERITY_SALT = "9w3uw0113u"
    JAZZCASH_RETURN_URL = "http://127.0.0.1:8000/payments/payment_status/"
    JAZZCASH_CURRENCY_CODE = "PKR"
    JAZZCASH_LANGUAGE = "EN"
    JAZZCASH_API_VERSION = 2.0
    JAZZCASH_T_TIMEOUT = timedelta(hours=24)
    JAZZCASH_HTTP_POST_URL = "https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/"

    def __init__(self, product, user, T_method="MWALLET"):
        self.amount = product.to_PKR() * 100
        self.product_id = product.id
        self.payment_method = T_method
        self.T_datetime = self.set_T_datetime()
        self.T_Expieration = self.set_T_Expieration()
        self.T_refernce_no = self.set_T_refernce_no()
        self.data = self.get_post_data()
        self.set_customer_info(user)
        self.create_secure_hash()

    def get_post_data(self):
        data = {
            "pp_Version": self.JAZZCASH_API_VERSION,
            "pp_IsRegisteredCustomer": "Yes",
            "pp_TxnType": self.payment_method,
            "pp_TokenizedCardNumber": "",
            "pp_CustomerID": "",
            "pp_CustomerEmail": "",
            "pp_CustomerMobile": "",
            "pp_MerchantID": self.JAZZCASH_MERCHANT_ID,
            "pp_SubMerchantID": "",
            "pp_Password": self.JAZZCASH_PASSWORD,
            "pp_TxnRefNo": self.T_refernce_no,
            "pp_Amount": self.amount,
            "pp_DiscountedAmount": "",
            "pp_DiscountBank": "",
            "pp_TxnCurrency": self.JAZZCASH_CURRENCY_CODE,
            "pp_TxnDateTime": self.T_datetime,
            "pp_TxnExpiryDateTime": self.T_Expieration,
            "pp_BillReference": "billRef",
            "pp_ReturnURL": self.JAZZCASH_RETURN_URL,
            "ppmpf_1": "1",
            "ppmpf_2": "2",
            "ppmpf_3": "3",
            "ppmpf_4": "4",
            "ppmpf_5": "5",
            "pp_BankID": "TBANK",
            "pp_Language": self.JAZZCASH_LANGUAGE,
            "pp_ProductID": self.product_id,
            "pp_Description": "Description of Transaction",
            "pp_SecureHash": "",
        }
        return data

    def set_T_refernce_no(self):
        start_time = self.T_datetime
        return "{0}{1}".format("T", start_time)

    def set_T_datetime(self):
        now = timezone.now()
        return self.TimeFormat(now)

    def set_T_Expieration(self):
        now = timezone.now()
        expiration_time = now + self.JAZZCASH_T_TIMEOUT
        return self.TimeFormat(expiration_time)

    def TimeFormat(self, obj):
        return obj.strftime("%Y%m%d%H%M%S")

    def create_secure_hash(self):
        stored_string = self.JAZZCASH_INTEGERITY_SALT
        for key in self.data:
            if self.data[key] != "":
                stored_string += "&"
                stored_string += str(self.data[key])
        signature = hmac.new(
            self.JAZZCASH_INTEGERITY_SALT.encode(),
            msg=stored_string.encode(),
            digestmod=hashlib.sha256,
        )
        self.data["pp_SecureHash"] = signature.hexdigest()

    def set_customer_info(self, user):
        self.data["pp_CustomerID"] = user.id
        self.data["pp_CustomerEmail"] = user.email
        self.data["pp_CustomerMobile"] = ""

    def set_return_url(self, course, user):
        self.data["pp_ReturnURL"] = "{}{}".format(
            "http://127.0.0.1:8000",
            reverse(
                "payments:payment_confirm",
                args=(course.id, user.id),
            ),
        )


def extract_transaction_data(request):
    data = {}
    data["Transaction_id"] = request.POST["pp_TxnRefNo"]
    data["Amount"] = int(request.POST["pp_Amount"]) // 100
    data["ResponseCode"] = request.POST["pp_ResponseCode"]
    data["ResponseMessage"] = request.POST["pp_ResponseMessage"]
    data["MerchantID"] = request.POST["pp_MerchantID"]
    data["SecureHash"] = request.POST["pp_SecureHash"]
    data["RetreivalReferenceNo"] = request.POST["pp_RetreivalReferenceNo"]
    return data


def validate_data(data, total_price):
    return all(data.values()) and total_price == data["Amount"]


def create_transaction(data, enrollment):
    transaction = Transaction.objects.create(
        transaction_id=data["Transaction_id"],
        transaction_retreival_reference_no=data["RetreivalReferenceNo"],
        total_amount=enrollment.course.to_PKR(),
        paid_amount=data["Amount"],
        status=check_payment_status(data["ResponseCode"]),
        enrollment=enrollment,
    )
    return transaction


def check_payment_status(response_code):
    if response_code == 000 or response_code == "000":
        return True
    else:
        return False
