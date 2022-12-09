from django.test import TestCase,Client
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY
from django.test import TestCase

class LogInTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='aaryan')
        user.set_password('123456')
        user.save()
    def test_login(self):
        c = Client()
        logged_in = c.login(username='aaryan', password='123456')
        self.assertEqual(logged_in, True)

# class DashboardTest(TestCase):
#     def setUp(self):
#         user = User.objects.create(username='aaryan')
#         user.set_password('123456')
#         user.save()
#     def test_dashboard(self):
#         driver.get("http://127.0.0.1:8000/accounts/login")
#         login = driver.find_element_by_id("id_login")
#         login.send_keys("aaryan.purohit")
#         password = driver.find_element_by_id("id_password")
#         passoword.send_keys("aaryan.purohit")


# driver.close()

        

