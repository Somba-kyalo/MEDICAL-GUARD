from rest_framework import serializers

from .models import Referral


class ReferralSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(
        source="patient.user.username",
        read_only=True,
    )
    amr_risk_level = serializers.CharField(
        source="amr_record.risk_level",
        read_only=True,
    )
    priority_display = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Referral
        fields = [
            "id",
            "patient",
            "patient_username",
            "amr_record",
            "amr_risk_level",
            "referral_reason",
            "clinical_summary",
            "destination_name",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "referral_notes",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]
