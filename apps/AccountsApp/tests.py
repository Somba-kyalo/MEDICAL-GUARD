from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class UserModelTests(TestCase):

    def test_user_defaults_to_patient_role(self):
        user = User.objects.create_user(
            username='patient1',
            password='TestPass123!',
        )

        self.assertEqual(user.role, User.Role.PATIENT)

    def test_user_password_is_hashed(self):
        user = User.objects.create_user(
            username='patient2',
            password='TestPass123!',
        )

        self.assertNotEqual(user.password, 'TestPass123!')
        self.assertTrue(user.check_password('TestPass123!'))


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='loginuser',
            password='TestPass123!',
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('AccountsApp:login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AccountsApp/login.html')

    def test_valid_login(self):
        response = self.client.post(
            reverse('AccountsApp:login'),
            {
                'username': 'loginuser',
                'password': 'TestPass123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:dashboard'),
        )

        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        response = self.client.post(
            reverse('AccountsApp:login'),
            {
                'username': 'loginuser',
                'password': 'WrongPassword!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AccountsApp/login.html')
        self.assertContains(
            response,
            'Invalid username or password.',
        )

    def test_authenticated_user_is_redirected_from_login(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('AccountsApp:login'),
        )

        self.assertRedirects(
            response,
            reverse('core:dashboard'),
        )


class RegistrationViewTests(TestCase):

    def test_registration_page_loads(self):
        response = self.client.get(
            reverse('AccountsApp:register'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'AccountsApp/register.html',
        )

    def test_patient_can_register(self):
        response = self.client.post(
            reverse('AccountsApp:register'),
            {
                'username': 'newpatient',
                'email': 'patient@example.com',
                'first_name': 'New',
                'last_name': 'Patient',
                'password': 'TestPass123!',
                'confirm_password': 'TestPass123!',
            },
        )

        user = User.objects.get(username='newpatient')

        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertEqual(user.email, 'patient@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Patient')
        self.assertTrue(user.check_password('TestPass123!'))

        self.assertRedirects(
            response,
            reverse('core:dashboard'),
        )

        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_rejects_missing_username(self):
        response = self.client.post(
            reverse('AccountsApp:register'),
            {
                'username': '',
                'password': 'TestPass123!',
                'confirm_password': 'TestPass123!',
            },
        )

        self.assertEqual(User.objects.count(), 0)
        self.assertContains(
            response,
            'Username and password are required.',
        )

    def test_registration_rejects_missing_password(self):
        response = self.client.post(
            reverse('AccountsApp:register'),
            {
                'username': 'patient3',
                'password': '',
                'confirm_password': '',
            },
        )

        self.assertEqual(User.objects.count(), 0)
        self.assertContains(
            response,
            'Username and password are required.',
        )

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse('AccountsApp:register'),
            {
                'username': 'patient4',
                'password': 'TestPass123!',
                'confirm_password': 'DifferentPass123!',
            },
        )

        self.assertEqual(User.objects.count(), 0)
        self.assertContains(
            response,
            'Passwords do not match.',
        )

    def test_registration_rejects_duplicate_username(self):
        User.objects.create_user(
            username='existinguser',
            password='TestPass123!',
        )

        response = self.client.post(
            reverse('AccountsApp:register'),
            {
                'username': 'existinguser',
                'password': 'TestPass123!',
                'confirm_password': 'TestPass123!',
            },
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertContains(
            response,
            'That username is already in use.',
        )

    def test_authenticated_user_is_redirected_from_registration(self):
        user = User.objects.create_user(
            username='authenticateduser',
            password='TestPass123!',
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('AccountsApp:register'),
        )

        self.assertRedirects(
            response,
            reverse('core:dashboard'),
        )


class ProfileViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            password='TestPass123!',
        )

    def test_authenticated_user_can_access_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('AccountsApp:profile'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'AccountsApp/profile.html',
        )
        self.assertContains(response, 'profileuser')

    def test_anonymous_user_is_redirected_from_profile(self):
        response = self.client.get(
            reverse('AccountsApp:profile'),
        )

        self.assertRedirects(
            response,
            f'{reverse("AccountsApp:login")}?next={reverse("AccountsApp:profile")}',
        )


class LogoutViewTests(TestCase):

    def test_logout_redirects_to_home(self):
        user = User.objects.create_user(
            username='logoutuser',
            password='TestPass123!',
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('AccountsApp:logout'),
        )

        self.assertRedirects(
            response,
            reverse('core:home'),
        )

        response = self.client.get(
            reverse('AccountsApp:profile'),
        )

        self.assertRedirects(
            response,
            f'{reverse("AccountsApp:login")}?next={reverse("AccountsApp:profile")}',
        )