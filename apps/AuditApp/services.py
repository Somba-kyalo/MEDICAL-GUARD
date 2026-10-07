from apps.AuditApp.models import AuditLog


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def create_audit_log(
    *,
    user=None,
    action,
    description,
    request=None,
    model_name="",
    object_id="",
    success=True,
):
    ip_address = None
    user_agent = ""

    if request is not None:
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else "",
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
    )


def log_login(user, request=None, success=True):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.LOGIN,
        description=f"User {user.username} logged in.",
        request=request,
        success=success,
    )


def log_logout(user, request=None):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.LOGOUT,
        description=f"User {user.username} logged out.",
        request=request,
    )


def log_create(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.CREATE,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_update(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.UPDATE,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_delete(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.DELETE,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_view(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.VIEW,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_review(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.REVIEW,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )


def log_complete(
    user,
    model_name,
    object_id,
    description,
    request=None,
):
    return create_audit_log(
        user=user,
        action=AuditLog.Action.COMPLETE,
        model_name=model_name,
        object_id=object_id,
        description=description,
        request=request,
    )
