from rest_framework import serializers

from .models import Facility, FacilityResource


class FacilityResourceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    class Meta:
        model = FacilityResource
        fields = [
            "id",
            "facility",
            "name",
            "category",
            "category_display",
            "quantity",
            "available",
            "notes",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class FacilitySerializer(serializers.ModelSerializer):
    facility_type_display = serializers.CharField(
        source="get_facility_type_display",
        read_only=True,
    )
    operating_status_display = serializers.CharField(
        source="get_operating_status_display",
        read_only=True,
    )
    resources = FacilityResourceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Facility
        fields = [
            "id",
            "name",
            "facility_code",
            "facility_type",
            "facility_type_display",
            "county",
            "sub_county",
            "address",
            "phone_number",
            "email",
            "latitude",
            "longitude",
            "services",
            "referral_available",
            "operating_status",
            "operating_status_display",
            "resources",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
