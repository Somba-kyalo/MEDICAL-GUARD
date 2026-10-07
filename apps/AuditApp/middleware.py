from apps.AuditApp.services import create_audit_log


class AuditMiddleware:
    EXCLUDED_PATHS = (
        "/static/",
        "/media/",
        "/favicon.ico",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self._should_log(request):
            self._create_request_log(request, response)

        return response

    def _should_log(self, request):
        if request.path.startswith(self.EXCLUDED_PATHS):
            return False

        if not request.user.is_authenticated:
            return False

        return request.method in {"POST", "PUT", "PATCH", "DELETE"}

    def _create_request_log(self, request, response):
        success = 200 <= response.status_code < 400

        create_audit_log(
            user=request.user,
            action=self._get_action(request.method),
            description=(
                f"{request.method} request to {request.path} "
                f"returned status {response.status_code}."
            ),
            request=request,
            success=success,
        )

    @staticmethod
    def _get_action(method):
        if method == "POST":
            return "CREATE"

        if method in {"PUT", "PATCH"}:
            return "UPDATE"

        if method == "DELETE":
            return "DELETE"

        return "OTHER"
