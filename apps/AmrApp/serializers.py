from rest_framework import serializers

from .models import AMRRecord, Antibiotic, Organism, ResistanceTest


class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
        ]


class AntibioticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antibiotic
        fields = [
            "id",
            "name",
            "code",
            "antibiotic_class",
            "is_active",
        ]


class ResistanceTestSerializer(serializers.ModelSerializer):
    organism_name = serializers.CharField(
        source="organism.name",
        read_only=True,
    )
    antibiotic_name = serializers.CharField(
        source="antibiotic.name",
        read_only=True,
    )
    result_display = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    class Meta:
        model = ResistanceTest
        fields = [
            "id",
            "amr_record",
            "organism",
            "organism_name",
            "antibiotic",
            "antibiotic_name",
            "result",
            "result_display",
            "test_notes",
            "tested_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class AMRRecordSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(
        source="patient.user.username",
        read_only=True,
    )
    screening_type = serializers.CharField(
        source="screening.get_screening_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    risk_level_display = serializers.CharField(
        source="get_risk_level_display",
        read_only=True,
    )
    resistance_tests = ResistanceTestSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = AMRRecord
        fields = [
            "id",
            "patient",
            "patient_username",
            "screening",
            "screening_type",
            "ai_analysis",
            "exposure_history",
            "infection_information",
            "risk_level",
            "risk_level_display",
            "clinical_notes",
            "status",
            "status_display",
            "resistance_tests",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]
