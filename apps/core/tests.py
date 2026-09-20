from django.test import TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):

    def test_home_page(self):
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_about_page(self):
        response = self.client.get(reverse('core:about'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_dashboard_page(self):
        response = self.client.get(reverse('core:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_error_page(self):
        response = self.client.get(reverse('core:error'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/error.html')