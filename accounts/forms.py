from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from main.models import Student


class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(), required=True, max_length=255)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"
