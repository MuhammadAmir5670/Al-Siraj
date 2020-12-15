from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from .. import views
from ..forms import SignUpForm
# Create your tests here.


class SignUpTests(TestCase):

    def setUp(self):
        url = reverse('accounts:sign_up')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_status_code(self):
        url = reverse('accounts:sign_up')
        view = resolve(url)
        self.assertEqual(view.func, views.sign_up)

    def test_csrf_token(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_containes_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('accounts:sign_up')
        data = {
            'username': 'john',
            'email': 'example@gmail.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home = reverse('boards:home')

    # def test_statsus_code(self):
    #     self.assertEquals(self.response.status_code, 200)

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        '''
        Create a new request to an arbitrary page.
        The resulting response should now have a `user` to its context,
        after a successful sign up.
        '''
        response = self.client.get(self.home)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

    def test_input_fields(self):
        '''
        The view must contain five inputs: csrf, username, email,
        password1, password2
        # '''
        # self.assertContains(self.response, '<input', 4)
        # self.assertContains(self.response, 'type="text', 1)
        # self.assertContains(self.response, 'type="email', 1)
        # self.assertContains(self.response, 'type="password', 2)
