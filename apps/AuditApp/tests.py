from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.AccountsApp.models import User
from apps.AuditApp.middleware import AuditMiddleware
from apps.AuditApp.models import AuditLog
from apps.AuditApp.services import (
    create_audit_log,
    get_client_ip,
    log_complete,
    log_create,
    log_delete,
    log_login,
    log_logout,
    log_review,
    log_update,
    log_view,
)


class AuditServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="audituser",
            password="StrongPassword123!",
            role=User.Role.CLINICIAN,
        )

        self.factory = RequestFactory()

    def test_create_audit_log(self):
        request = self.factory.get(
            "/test/",
            HTTP_USER_AGENT="Test Browser",
            REMOTE_ADDR="127.0.0.1",
        )

        audit = create_audit_log(
            user=self.user,
            action=AuditLog.Action.VIEW,
            description="Viewed patient record.",
            request=request,
            model_name="Patient",
            object_id=1,
        )

        self.assertEqual(audit.user, self.user)
        self.assertEqual(audit.action, AuditLog.Action.VIEW)
        self.assertEqual(audit.model_name, "Patient")
        self.assertEqual(audit.object_id, "1")
        self.assertEqual(audit.ip_address, "127.0.0.1")
        self.assertEqual(audit.user_agent, "Test Browser")
        self.assertTrue(audit.success)

    def test_forwarded_ip_is_detected(self):
        request = self.factory.get(
            "/test/",
            HTTP_X_FORWARDED_FOR="192.168.1.10, 10.0.0.1",
        )

        self.assertEqual(get_client_ip(request), "192.168.1.10")

    def test_login_log(self):
        audit = log_login(self.user)

        self.assertEqual(audit.action, AuditLog.Action.LOGIN)
        self.assertEqual(audit.user, self.user)

    def test_logout_log(self):
        audit = log_logout(self.user)

        self.assertEqual(audit.action, AuditLog.Action.LOGOUT)

    def test_create_log(self):
        audit = log_create(
            self.user,
            "Patient",
            10,
            "Created patient record.",
        )

        self.assertEqual(audit.action, AuditLog.Action.CREATE)
        self.assertEqual(audit.model_name, "Patient")
        self.assertEqual(audit.object_id, "10")

    def test_update_log(self):
        audit = log_update(
            self.user,
            "Patient",
            10,
            "Updated patient record.",
        )

        self.assertEqual(audit.action, AuditLog.Action.UPDATE)

    def test_delete_log(self):
        audit = log_delete(
            self.user,
            "Patient",
            10,
            "Deleted patient record.",
        )

        self.assertEqual(audit.action, AuditLog.Action.DELETE)

    def test_view_log(self):
        audit = log_view(
            self.user,
            "Patient",
            10,
            "Viewed patient record.",
        )

        self.assertEqual(audit.action, AuditLog.Action.VIEW)

    def test_review_log(self):
        audit = log_review(
            self.user,
            "Screening",
            20,
            "Reviewed screening.",
        )

        self.assertEqual(audit.action, AuditLog.Action.REVIEW)

    def test_complete_log(self):
        audit = log_complete(
            self.user,
            "FollowUp",
            30,
            "Completed follow-up.",
        )

        self.assertEqual(audit.action, AuditLog.Action.COMPLETE)


class AuditMiddlewareTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="middlewareuser",
            password="StrongPassword123!",
            role=User.Role.CLINICIAN,
        )

        self.factory = RequestFactory()

    def get_response(self, request):
        from django.http import JsonResponse

        return JsonResponse({"status": "ok"}, status=200)

    def get_failed_response(self, request):
        from django.http import JsonResponse

        return JsonResponse({"status": "error"}, status=400)

    def authenticate_request(self, request):
        request.user = self.user
        return request

    def test_post_request_creates_create_audit(self):
        request = self.authenticate_request(
            self.factory.post(
                "/patients/create/",
                HTTP_USER_AGENT="Test Browser",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        audit = AuditLog.objects.get()

        self.assertEqual(audit.action, AuditLog.Action.CREATE)
        self.assertEqual(audit.user, self.user)
        self.assertTrue(audit.success)

    def test_put_request_creates_update_audit(self):
        request = self.authenticate_request(
            self.factory.put(
                "/patients/1/",
                HTTP_USER_AGENT="Test Browser",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        audit = AuditLog.objects.get()

        self.assertEqual(audit.action, AuditLog.Action.UPDATE)

    def test_patch_request_creates_update_audit(self):
        request = self.authenticate_request(
            self.factory.patch(
                "/patients/1/",
                HTTP_USER_AGENT="Test Browser",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        audit = AuditLog.objects.get()

        self.assertEqual(audit.action, AuditLog.Action.UPDATE)

    def test_delete_request_creates_delete_audit(self):
        request = self.authenticate_request(
            self.factory.delete(
                "/patients/1/",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        audit = AuditLog.objects.get()

        self.assertEqual(audit.action, AuditLog.Action.DELETE)

    def test_failed_request_is_recorded_as_unsuccessful(self):
        request = self.authenticate_request(
            self.factory.post(
                "/patients/create/",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_failed_response)
        middleware(request)

        audit = AuditLog.objects.get()

        self.assertFalse(audit.success)

    def test_get_request_is_not_audited(self):
        request = self.authenticate_request(
            self.factory.get(
                "/patients/",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(AuditLog.objects.count(), 0)

    def test_unauthenticated_request_is_not_audited(self):
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.post(
            "/patients/create/",
            REMOTE_ADDR="127.0.0.1",
        )
        request.user = AnonymousUser()

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(AuditLog.objects.count(), 0)

    def test_static_request_is_not_audited(self):
        request = self.authenticate_request(
            self.factory.post(
                "/static/test/",
                REMOTE_ADDR="127.0.0.1",
            )
        )

        middleware = AuditMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(AuditLog.objects.count(), 0)
