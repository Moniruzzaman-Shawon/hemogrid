from django.urls import reverse
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    FRONTEND_URL="http://testserver",
)
class RegisterViewTests(APITestCase):
    def test_user_can_register_and_email_is_sent(self):
        url = reverse("auth:register")
        payload = {
            "email": "NewUser@Example.com",
            "password": "StrongPass!234",
            "full_name": "New User",
            "age": 30,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["email"], payload["email"].lower())
        self.assertEqual(response.data["full_name"], payload["full_name"])
        self.assertEqual(response.data["age"], payload["age"])

        user = User.objects.get(email=payload["email"].lower())
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.full_name, payload["full_name"])
        self.assertEqual(user.age, payload["age"])

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn(payload["email"].lower(), sent_mail.to)
        self.assertIn("Verify your Hemogrid account", sent_mail.subject)
        self.assertIn("http://testserver/verify-email/", sent_mail.body)

    def test_registration_email_falls_back_to_backend_url(self):
        mail.outbox.clear()
        url = reverse("auth:register")
        payload = {
            "email": "fallback@example.com",
            "password": "AnotherStrongPass!234",
            "full_name": "Backend Link",
            "age": 28,
        }

        with override_settings(FRONTEND_URL=None, EMAIL_VERIFICATION_BASE_URL=None):
            response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertIn("http://testserver/api/auth/verify-email/", sent_mail.body)
