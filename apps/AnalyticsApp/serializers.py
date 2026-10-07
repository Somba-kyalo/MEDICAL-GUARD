from rest_framework import serializers


class PatientStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    male = serializers.IntegerField()
    female = serializers.IntegerField()


class ScreeningStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    under_review = serializers.IntegerField()
    reviewed = serializers.IntegerField()
    by_type = serializers.ListField()


class ScreeningRiskStatisticsSerializer(serializers.Serializer):
    low = serializers.IntegerField()
    moderate = serializers.IntegerField()
    high = serializers.IntegerField()
    urgent = serializers.IntegerField()


class AMRStatisticsSerializer(serializers.Serializer):
    records = serializers.IntegerField()
    open = serializers.IntegerField()
    under_review = serializers.IntegerField()
    reviewed = serializers.IntegerField()
    closed = serializers.IntegerField()
    high_risk = serializers.IntegerField()
    urgent = serializers.IntegerField()
    resistance_tests = serializers.IntegerField()
    resistant_tests = serializers.IntegerField()


class ResistanceStatisticsSerializer(serializers.Serializer):
    susceptible = serializers.IntegerField()
    intermediate = serializers.IntegerField()
    resistant = serializers.IntegerField()
    unknown = serializers.IntegerField()
    by_organism = serializers.ListField()
    by_antibiotic = serializers.ListField()


class ReferralStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    sent = serializers.IntegerField()
    accepted = serializers.IntegerField()
    declined = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    emergency = serializers.IntegerField()
    urgent = serializers.IntegerField()


class FacilityStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    temporarily_closed = serializers.IntegerField()
    referral_available = serializers.IntegerField()


class FollowUpStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    completed = serializers.IntegerField()
    missed = serializers.IntegerField()
    rescheduled = serializers.IntegerField()


class DashboardStatisticsSerializer(serializers.Serializer):
    patients = PatientStatisticsSerializer()
    screening = ScreeningStatisticsSerializer()
    screening_risk = ScreeningRiskStatisticsSerializer()
    amr = AMRStatisticsSerializer()
    resistance = ResistanceStatisticsSerializer()
    referrals = ReferralStatisticsSerializer()
    facilities = FacilityStatisticsSerializer()
    follow_ups = FollowUpStatisticsSerializer()
