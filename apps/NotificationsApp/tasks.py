from django.utils import timezone

from apps.NotificationsApp.models import Notification
from apps.NotificationsApp.services import create_notification
from apps.FollowupsApp.models import FollowUp


def create_follow_up_reminders():
    now = timezone.now()

    follow_ups = FollowUp.objects.select_related(
        "patient",
        "referral",
        "created_by",
    ).filter(
        scheduled_at__lte=now,
        status=FollowUp.Status.PENDING,
    )

    created_count = 0

    for follow_up in follow_ups:
        existing = Notification.objects.filter(
            recipient=follow_up.created_by,
            follow_up=follow_up,
            notification_type=Notification.NotificationType.FOLLOW_UP_REMINDER,
        ).exists()

        if existing:
            continue

        create_notification(
            recipient=follow_up.created_by,
            notification_type=Notification.NotificationType.FOLLOW_UP_REMINDER,
            title="Follow-up Reminder",
            message=f"Follow-up for {follow_up.patient} is due.",
            priority=Notification.Priority.HIGH,
            patient=follow_up.patient,
            referral=follow_up.referral,
            follow_up=follow_up,
            action_url=f"/followups/detail/{follow_up.id}/",
        )

        created_count += 1

    return created_count


def mark_missed_follow_ups():
    now = timezone.now()

    follow_ups = FollowUp.objects.select_related(
        "patient",
        "referral",
        "created_by",
    ).filter(
        scheduled_at__lt=now,
        status=FollowUp.Status.PENDING,
    )

    updated_count = 0

    for follow_up in follow_ups:
        follow_up.status = FollowUp.Status.MISSED
        follow_up.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        existing = Notification.objects.filter(
            recipient=follow_up.created_by,
            follow_up=follow_up,
            notification_type=Notification.NotificationType.FOLLOW_UP_MISSED,
        ).exists()

        if not existing:
            create_notification(
                recipient=follow_up.created_by,
                notification_type=Notification.NotificationType.FOLLOW_UP_MISSED,
                title="Follow-up Missed",
                message=f"Follow-up for {follow_up.patient} has been marked as missed.",
                priority=Notification.Priority.HIGH,
                patient=follow_up.patient,
                referral=follow_up.referral,
                follow_up=follow_up,
                action_url=f"/followups/detail/{follow_up.id}/",
            )

        updated_count += 1

    return updated_count
