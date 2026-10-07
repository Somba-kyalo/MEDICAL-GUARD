from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.NotificationsApp.models import Notification
from apps.NotificationsApp.services import (
    create_amr_alert,
    create_follow_up_notification,
    create_notification,
    create_referral_notification,
    delete_all_read_notifications,
    get_notification,
    get_notifications_by_priority,
    get_notifications_by_type,
    get_read_notifications,
    get_unread_notifications,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
    mark_notification_as_unread,
)

from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral
from apps.FollowupsApp.models import FollowUp

User = get_user_model()


class NotificationTestDataMixin:
    def create_user(self, username):
        return User.objects.create_user(
            username=username,
            password="TestPass123!",
            role=User.Role.CLINICIAN,
        )

    def create_patient(self, user):
        return Patient.objects.create(
            user=user,
            date_of_birth=date(2000, 1, 1),
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Voi",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0798765432",
        )


class NotificationModelTests(
    NotificationTestDataMixin,
    TestCase,
):
    def setUp(self):
        self.user = self.create_user("clinician1")

    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="System Alert",
            message="System maintenance scheduled.",
        )

        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)
        self.assertEqual(
            notification.priority,
            Notification.Priority.NORMAL,
        )

    def test_notification_string(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Test Notification",
            message="Test message.",
        )

        self.assertEqual(
            str(notification),
            "Test Notification - clinician1",
        )


class NotificationServiceTests(
    NotificationTestDataMixin,
    TestCase,
):
    def setUp(self):
        self.user = self.create_user("clinician1")
        self.other_user = self.create_user("clinician2")

        self.patient = self.create_patient(self.create_user("patient1"))

    def test_create_notification_service(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="System Alert",
            message="Important system message.",
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

    def test_invalid_notification_type(self):
        with self.assertRaises(Exception):
            create_notification(
                recipient=self.user,
                notification_type="INVALID",
                title="Test",
                message="Test message",
            )

    def test_invalid_priority(self):
        with self.assertRaises(Exception):
            create_notification(
                recipient=self.user,
                notification_type=Notification.NotificationType.SYSTEM_ALERT,
                title="Test",
                message="Test message",
                priority="INVALID",
            )

    def test_get_user_notifications(self):
        create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="User Notification",
            message="Message",
        )

        create_notification(
            recipient=self.other_user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Other Notification",
            message="Message",
        )

        notifications = get_user_notifications(self.user)

        self.assertEqual(notifications.count(), 1)
        self.assertEqual(
            notifications.first().title,
            "User Notification",
        )

    def test_get_unread_notifications(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Unread",
            message="Message",
        )

        self.assertEqual(
            get_unread_notifications(self.user).count(),
            1,
        )

        mark_notification_as_read(notification)

        self.assertEqual(
            get_unread_notifications(self.user).count(),
            0,
        )

    def test_get_read_notifications(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Read",
            message="Message",
        )

        mark_notification_as_read(notification)

        self.assertEqual(
            get_read_notifications(self.user).count(),
            1,
        )

    def test_get_notifications_by_type(self):
        create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.AMR_ALERT,
            title="AMR Alert",
            message="Message",
        )

        create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="System Alert",
            message="Message",
        )

        notifications = get_notifications_by_type(
            self.user,
            Notification.NotificationType.AMR_ALERT,
        )

        self.assertEqual(notifications.count(), 1)
        self.assertEqual(
            notifications.first().title,
            "AMR Alert",
        )

    def test_get_notifications_by_priority(self):
        create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Critical",
            message="Message",
            priority=Notification.Priority.CRITICAL,
        )

        notifications = get_notifications_by_priority(
            self.user,
            Notification.Priority.CRITICAL,
        )

        self.assertEqual(notifications.count(), 1)

    def test_mark_notification_as_read(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Test",
            message="Message",
        )

        mark_notification_as_read(notification)

        notification.refresh_from_db()

        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_mark_notification_as_unread(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Test",
            message="Message",
        )

        mark_notification_as_read(notification)
        mark_notification_as_unread(notification)

        notification.refresh_from_db()

        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

    def test_mark_all_notifications_as_read(self):
        for index in range(3):
            create_notification(
                recipient=self.user,
                notification_type=Notification.NotificationType.SYSTEM_ALERT,
                title=f"Notification {index}",
                message="Message",
            )

        updated_count = mark_all_notifications_as_read(self.user)

        self.assertEqual(updated_count, 3)
        self.assertEqual(
            get_unread_notifications(self.user).count(),
            0,
        )

    def test_delete_all_read_notifications(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Read",
            message="Message",
        )

        mark_notification_as_read(notification)

        deleted_count = delete_all_read_notifications(self.user)

        self.assertEqual(deleted_count, 1)
        self.assertEqual(
            Notification.objects.count(),
            0,
        )

    def test_get_notification(self):
        notification = create_notification(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Test",
            message="Message",
        )

        result = get_notification(notification.id)

        self.assertEqual(result.id, notification.id)

    def test_create_amr_alert(self):
        notification = create_amr_alert(
            recipient=self.user,
            patient=self.patient,
            title="AMR Alert",
            message="Resistance alert.",
        )

        self.assertEqual(
            notification.notification_type,
            Notification.NotificationType.AMR_ALERT,
        )
        self.assertEqual(
            notification.patient,
            self.patient,
        )

    def test_create_referral_notification(self):
        referral = Referral.objects.create(
            patient=self.patient,
            referral_reason="Specialist review",
            clinical_summary="Requires specialist review.",
            created_by=self.user,
        )

        notification = create_referral_notification(
            recipient=self.user,
            referral=referral,
            title="Referral Created",
            message="New referral created.",
        )

        self.assertEqual(
            notification.referral,
            referral,
        )
        self.assertEqual(
            notification.patient,
            self.patient,
        )


class NotificationViewTests(
    NotificationTestDataMixin,
    TestCase,
):
    def setUp(self):
        self.user = self.create_user("clinician1")
        self.other_user = self.create_user("clinician2")

        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="System Alert",
            message="System message.",
        )

    def test_list_page_requires_login(self):
        response = self.client.get(reverse("NotificationsApp:list"))

        self.assertEqual(response.status_code, 302)

    def test_list_page_authenticated(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.get(reverse("NotificationsApp:list"))

        self.assertEqual(response.status_code, 200)

    def test_unread_page_authenticated(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.get(reverse("NotificationsApp:unread"))

        self.assertEqual(response.status_code, 200)

    def test_all_notifications_api(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.get(reverse("NotificationsApp:api_records"))

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 1)

    def test_unread_notifications_api(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.get(reverse("NotificationsApp:api_unread"))

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 1)

    def test_mark_notification_read(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.post(
            reverse(
                "NotificationsApp:api_mark_read",
                args=[self.notification.id],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.notification.refresh_from_db()

        self.assertTrue(self.notification.is_read)

    def test_mark_notification_unread(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        self.notification.is_read = True
        self.notification.save()

        response = self.client.post(
            reverse(
                "NotificationsApp:api_mark_unread",
                args=[self.notification.id],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.notification.refresh_from_db()

        self.assertFalse(self.notification.is_read)

    def test_mark_all_read(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.SYSTEM_ALERT,
            title="Second",
            message="Message",
        )

        response = self.client.post(reverse("NotificationsApp:api_mark_all_read"))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.user,
                is_read=False,
            ).count(),
            0,
        )

    def test_delete_notification(self):
        self.client.login(
            username="clinician1",
            password="TestPass123!",
        )

        response = self.client.post(
            reverse(
                "NotificationsApp:api_delete",
                args=[self.notification.id],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(Notification.objects.filter(id=self.notification.id).exists())

    def test_user_cannot_access_other_users_notification(self):
        self.client.login(
            username="clinician2",
            password="TestPass123!",
        )

        response = self.client.get(
            reverse(
                "NotificationsApp:api_detail",
                args=[self.notification.id],
            )
        )

        self.assertEqual(response.status_code, 404)
