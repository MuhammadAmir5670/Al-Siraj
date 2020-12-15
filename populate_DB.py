import django, os, csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_learning_system.settings")
django.setup()

from main.models import Course, Currency


Currency.objects.create(currency_name="$", currency_value=160)
Currency.objects.create(currency_name="€", currency_value=194)
Currency.objects.create(currency_name="£", currency_value=215)


currencies = Currency.objects.all()
DOLLOR = currencies[0]
EURO = currencies[1]
POUND = currencies[2]


def get_currency_obj(currency):
    """
    method for returning the correct DB object
    """
    if currency == "$":
        return DOLLOR
    elif currency == "£":
        return POUND
    elif currency == "€":
        return EURO
    else:
        return None


def populate_database(file_name):
    """
    method for fetching data from file and populating the
    database
    """
    with open(file_name, "r") as file:
        reader = csv.DictReader(file)
        for obj in reader:
            currency = get_currency_obj(currency=obj["currency"])
            print(currency)
            if not currency:
                print("=" * 40)
                print("ERROR")
                print("=" * 40)
                return None
            else:
                print("Populating database")
                Course.objects.create(
                    course_name=obj["course_name"],
                    classes_per_week=obj["classes_per_week"],
                    class_duration=obj["class_duration"],
                    country=obj["country"],
                    pricing=obj["pricing"],
                    currency=currency,
                )


def main():
    populate_database("./Data/Quran_with_tajweed.csv")
    populate_database("./Data/noorani_qauida.csv")
    populate_database("./Data/islam_for_kids.csv")
    print(os.getcwd())


if __name__ == "__main__":
    main()