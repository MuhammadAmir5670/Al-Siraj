from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Currency)
admin.site.register(Enrollment)
admin.site.register(Trial)