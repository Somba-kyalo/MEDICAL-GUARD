from rest_framework import serializers

from apps.NotificationsApp.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True,
    )

    priority_display = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )

    recipient_name = serializers.CharField(
        source="recipient.username",
        read_only=True,
    )

    patient_name = serializers.CharField(
        source="patient.user.username",
        read_only=True,
        allow_null=True,
    )

    referral_id = serializers.IntegerField(
        source="referral.id",
        read_only=True,
        allow_null=True,
    )

    follow_up_id = serializers.IntegerField(
        source="follow_up.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notification

        fields = [
            "id",
            "recipient",
            "recipient_name",
            "notification_type",
            "notification_type_display",
            "title",
            "message",
            "priority",
            "priority_display",
            "patient",
            "patient_name",
            "referral",
            "referral_id",
            "follow_up",
            "follow_up_id",
            "action_url",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "recipient_name",
            "notification_type_display",
            "priority_display",
            "patient_name",
            "referral_id",
            "follow_up_id",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Notification title is required.")

        return value

    def validate_message(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Notification message is required.")

        return value
