from rest_framework import serializers

from apps.FollowupsApp.models import FollowUp


class FollowUpSerializer(serializers.ModelSerializer):
    follow_up_type_display = serializers.CharField(
        source="get_follow_up_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    patient_name = serializers.CharField(
        source="patient.user.username",
        read_only=True,
    )

    referral_id = serializers.IntegerField(
        source="referral.id",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = FollowUp
        fields = [
            "id",
            "patient",
            "patient_name",
            "referral",
            "referral_id",
            "follow_up_type",
            "follow_up_type_display",
            "reason",
            "scheduled_at",
            "status",
            "status_display",
            "outcome",
            "notes",
            "completed_at",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "patient_name",
            "referral_id",
            "follow_up_type_display",
            "status_display",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    def validate_reason(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Follow-up reason is required.")

        return value

    def validate(self, attrs):
        status = attrs.get(
            "status",
            getattr(self.instance, "status", FollowUp.Status.PENDING),
        )

        completed_at = attrs.get(
            "completed_at",
            getattr(self.instance, "completed_at", None),
        )

        if status == FollowUp.Status.COMPLETED and completed_at is None:
            raise serializers.ValidationError(
                {
                    "completed_at": (
                        "Completed follow-ups must have a completion date and time."
                    )
                }
            )

        return attrs
