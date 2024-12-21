import os
import django

from django.test import TestCase
from django.conf import settings

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, override_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venturebuild.settings')
django.setup()

from venturebuild import settings

# User = get_user_model()


# Create your tests here.
# class LoginTestCase(TestCase):
#     def setUp(self):
#         self.password = 'test1234'
#         self.email = 'bowale.adetunji@mail.utoronto.ca'  #Test email
#         self.user, created = User.objects.get_or_create(
#             email=self.email,
#             defaults={'password': self.password, 'first_name': 'test', 'last_name': '1'}
#         )
#
#     # def test_login(self):
#     #     login_url = '/login/'
#     #     response = self.client.post(login_url, {'email': self.email, 'password': self.password})
#     #
#     #     self.assertEquals(response.status_code, 200)
#     #     self.assertTrue(response.url, reverse('home'))
#     #     self.assertTrue(self.client.login(email=self.email, password=self.password))
#
#     @override_settings(ALLOWED_HOSTS=['testserver'])
#     class MyTestCase(TestCase):
#         def test_login_view(self):
#             response = self.client.post('/login/', {'username': 'test', 'password': 'test'})
#             self.assertEqual(response.status_code, 200)
