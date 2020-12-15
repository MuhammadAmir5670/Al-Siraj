from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('accounts:password_reset')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/accounts/reset/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input ', 2)
        self.assertContains(self.response, 'type="email"', 1)
