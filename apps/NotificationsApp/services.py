from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.NotificationsApp.models import Notification


def validate_notification_type(notification_type):
    valid_types = {choice[0] for choice in Notification.NotificationType.choices}

    if notification_type not in valid_types:
        raise ValidationError("Invalid notification type.")

    return notification_type


def validate_priority(priority):
    valid_priorities = {choice[0] for choice in Notification.Priority.choices}

    if priority not in valid_priorities:
        raise ValidationError("Invalid notification priority.")

    return priority


def create_notification(
    recipient,
    notification_type,
    title,
    message,
    priority=Notification.Priority.NORMAL,
    patient=None,
    referral=None,
    follow_up=None,
    action_url="",
):
    validate_notification_type(notification_type)
    validate_priority(priority)

    if not title or not title.strip():
        raise ValidationError("Notification title is required.")

    if not message or not message.strip():
        raise ValidationError("Notification message is required.")

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title.strip(),
        message=message.strip(),
        priority=priority,
        patient=patient,
        referral=referral,
        follow_up=follow_up,
        action_url=action_url.strip() if action_url else "",
    )


def get_notification(notification_id):
    return Notification.objects.select_related(
        "recipient",
        "patient",
        "patient__user",
        "referral",
        "follow_up",
    ).get(id=notification_id)


def get_user_notifications(user):
    return (
        Notification.objects.select_related(
            "recipient",
            "patient",
            "patient__user",
            "referral",
            "follow_up",
        )
        .filter(recipient=user)
        .order_by("-created_at")
    )


def get_unread_notifications(user):
    return get_user_notifications(user).filter(is_read=False)


def get_read_notifications(user):
    return get_user_notifications(user).filter(is_read=True)


def get_notifications_by_type(user, notification_type):
    validate_notification_type(notification_type)

    return get_user_notifications(user).filter(notification_type=notification_type)


def get_notifications_by_priority(user, priority):
    validate_priority(priority)

    return get_user_notifications(user).filter(priority=priority)


def mark_notification_as_read(notification):
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(
            update_fields=[
                "is_read",
                "read_at",
                "updated_at",
            ]
        )

    return notification


def mark_notification_as_unread(notification):
    notification.is_read = False
    notification.read_at = None
    notification.save(
        update_fields=[
            "is_read",
            "read_at",
            "updated_at",
        ]
    )

    return notification


def mark_all_notifications_as_read(user):
    now = timezone.now()

    updated_count = Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).update(
        is_read=True,
        read_at=now,
        updated_at=now,
    )

    return updated_count


def delete_notification(notification):
    notification.delete()


def delete_all_read_notifications(user):
    deleted_count, _ = Notification.objects.filter(
        recipient=user,
        is_read=True,
    ).delete()

    return deleted_count


def create_referral_notification(
    recipient,
    referral,
    title,
    message,
    notification_type=Notification.NotificationType.REFERRAL_CREATED,
    priority=Notification.Priority.NORMAL,
):
    return create_notification(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        patient=referral.patient,
        referral=referral,
        action_url=f"/referrals/detail/{referral.id}/",
    )


def create_follow_up_notification(
    recipient,
    follow_up,
    title,
    message,
    notification_type=Notification.NotificationType.FOLLOW_UP_CREATED,
    priority=Notification.Priority.NORMAL,
):
    return create_notification(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        patient=follow_up.patient,
        referral=follow_up.referral,
        follow_up=follow_up,
        action_url=f"/followups/detail/{follow_up.id}/",
    )


def create_amr_alert(
    recipient,
    patient,
    title,
    message,
    priority=Notification.Priority.HIGH,
):
    return create_notification(
        recipient=recipient,
        notification_type=Notification.NotificationType.AMR_ALERT,
        title=title,
        message=message,
        priority=priority,
        patient=patient,
    )
