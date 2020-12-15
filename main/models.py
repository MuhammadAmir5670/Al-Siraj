from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.shortcuts import Http404, get_object_or_404


from datetime import timedelta


# Create your models here.


class Currency(models.Model):
    currencies = [
        ("$", "Dollors"),
        ("€", "Euros"),
        ("£", "Pounds"),
    ]

    currency_name = models.CharField(
        max_length=1,
        choices=currencies,
        default="$",
    )
    currency_value = models.IntegerField(null=False, blank=False, default=100)

    def __str__(self):
        return self.currency_name


class Course(models.Model):
    counteries = [
        ("US", "United States / America"),
        ("EU", "Europe"),
        ("UK", "United Kingdom"),
        ("CA", "Canada"),
        ("OT", "Other"),
    ]

    course_name = models.CharField(max_length=70)
    classes_per_week = models.IntegerField(default=2)
    class_duration = models.IntegerField(default=30)
    country = models.CharField(
        max_length=2,
        choices=counteries,
        default="OT",
    )
    pricing = models.IntegerField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    user = models.ManyToManyField(
        User,
        through="Enrollment",
        through_fields=("course", "user"),
        editable=False,
    )

    def classes_per_month(self):
        """
        method for calculating classes per month
        """
        return self.classes_per_week * 4

    def get_course(self, course_id):
        """
        getting courses
        """
        if course_id == 1:
            return (
                self.objects.filter(course_name="quran with tajweed"),
                "quran with tajweed",
            )
        elif course_id == 2:
            return (self.objects.filter(course_name="islam for kids"), "islam for kids")
        elif course_id == 3:
            return (self.objects.filter(course_name="noorani qauida"), "noorani qauida")
        else:
            raise Http404("Invalid Request, Course not Found......")

    def seperate_query_sets(self, query_set):
        _US = query_set.filter(country="US")
        _UK = query_set.filter(country="UK")
        _CA = query_set.filter(country="CA")
        _EU = query_set.filter(country="EU")
        return {"US": _US, "UK": _UK, "CA": _CA, "EU": _EU}

    def to_PKR(self):
        return self.currency.currency_value * self.pricing

    def __str__(self):
        return "{} | {}".format(self.course_name, self.country)


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, editable=False, related_name="student"
    )
    profile_image = models.ImageField(null=True, blank=True, default="person-icon.png")
    email_confirmed = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        print("Created Student")
        if created:
            Student.objects.create(user=instance)
        instance.student.save()

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.student.save()

    def get_students(self, _type=None):
        if not _type:
            return User.objects.filter(groups__name="students")
        else:
            return User.objects.filter(groups__name=_type)

    def __str__(self):
        return self.user.username


class Trial(models.Model):
    status = models.BooleanField(default=True)
    started_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="trial"
    )
    course = models.CharField(max_length=150, null=True)

    def trial_available(self):
        return self.status

    def set_trial_datetime(self):
        now = timezone.now()
        period = timedelta(days=3)
        self.started_date = now
        self.end_date = now + period

    def get_active_trialies(self):
        now = timezone.now()
        return self.objects.filter(end_date__gt=now).exclude(user__groups__id=4)

    def get_inactive_trialies(self):
        now = timezone.now()
        return self.objects.filter(end_date__lt=now).exclude(user__groups__id=4)

    def deactive_trialies(self):
        now = timezone.now()
        trialies = self.get_inactive_trialies(self)
        for trialy in trialies:
            trialy.completed = True

    def get_trials(self):
        return self.objects.all().exclude(user__groups__id=4)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        print("Created Trial")
        if created:
            Trial.objects.create(user=instance)
        instance.trial.save()

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.student.save()

    def trial_status(self):
        return self.end_date > timezone.now()


class Enrollment(models.Model):
    def set_expiery():
        period = timedelta(days=30)
        return timezone.now() + period

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    expiries_at = models.DateTimeField(default=set_expiery)

    def user_enrollments(self, user_id):
        return self.objects.filter(user__id=user_id)

    def get_enrollment(self, user_id, enrollment_id):
        enrollment = self.objects.filter(id=enrollment_id, user__id=user_id)
        if enrollment:
            return enrollment[0]
        else:
            raise Http404("Page Not found")

    def get_enrollments(self):
        return self.objects.all()

    def active_enrollments(self):
        now = timezone.now()
        return self.objects.filter(expiries_at__gt=now)

    def inactive_enrollments(self):
        now = timezone.now()
        return self.objects.filter(expiries_at__lt=now)

    def deactivate_enrollments(self):
        now = timezone.now()
        trialies = self.inactive_enrollments(self)
        for trialy in trialies:
            trialy.completed = True

    def enrollment_status(self):
        return self.expiries_at > timezone.now()


def add_user_to_group(group_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    group = get_object_or_404(Group, pk=group_id)
    group.user_set.add(user)


def remove_user_from_group(group_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    group = get_object_or_404(Group, pk=group_id)
    user.groups.remove(group)


def get_data_for_admin():
    students = {
        "students": Student.get_students(Student).count(),
        "enrolled": Student.get_students(Student, _type="enroll_students").count(),
        "on_trial": Student.get_students(Student, _type="students_on_trial").count(),
    }
    enrollments = {
        "all": Enrollment.get_enrollments(Enrollment).count(),
        "active": Enrollment.active_enrollments(Enrollment).count(),
        "inactive": Enrollment.inactive_enrollments(Enrollment).count(),
    }
    return {
        "students": students,
        "enrollments": enrollments,
    }


def get_students(_type=None):
    if not _type:
        return Enrollment.objects.all().exculde(user__groups__id=4)
    elif _type == "students_on_trial":
        return Student.get_students(Student, _type="students_on_trial")
    elif _type == "active":
        return Enrollment.active_enrollments(Enrollment)
    elif _type == "inactive":
        return Enrollment.inactive_enrollments(Enrollment)
    else:
        raise Http404("Page Not Found")


def get_user_enrollment_count():
    users = User.objects.all().exclude(groups__id=4)
    counts = []
    for user in users:
        counts.append(Enrollment.user_enrollments(Enrollment, user.id).count())
    return counts