from django.db.models import Count

from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening
from apps.AmrApp.models import AMRRecord, ResistanceTest
from apps.ReferralsApp.models import Referral
from apps.FacilitiesApp.models import Facility
from apps.FollowupsApp.models import FollowUp


def patient_statistics():
    return {
        "total": Patient.objects.count(),
        "male": Patient.objects.filter(sex=Patient.Sex.MALE).count(),
        "female": Patient.objects.filter(sex=Patient.Sex.FEMALE).count(),
    }


def screening_statistics():
    return {
        "total": Screening.objects.count(),
        "completed": Screening.objects.filter(
            status=Screening.Status.COMPLETED
        ).count(),
        "in_progress": Screening.objects.filter(
            status=Screening.Status.IN_PROGRESS
        ).count(),
        "under_review": Screening.objects.filter(
            status=Screening.Status.UNDER_REVIEW
        ).count(),
        "reviewed": Screening.objects.filter(status=Screening.Status.REVIEWED).count(),
        "by_type": list(
            Screening.objects.values("screening_type")
            .annotate(total=Count("id"))
            .order_by("screening_type")
        ),
    }


def screening_risk_statistics():
    return {
        "low": Screening.objects.filter(assessment__risk_level="LOW").count(),
        "moderate": Screening.objects.filter(assessment__risk_level="MODERATE").count(),
        "high": Screening.objects.filter(assessment__risk_level="HIGH").count(),
        "urgent": Screening.objects.filter(assessment__risk_level="URGENT").count(),
    }


def amr_statistics():
    return {
        "records": AMRRecord.objects.count(),
        "open": AMRRecord.objects.filter(status=AMRRecord.Status.OPEN).count(),
        "under_review": AMRRecord.objects.filter(
            status=AMRRecord.Status.UNDER_REVIEW
        ).count(),
        "reviewed": AMRRecord.objects.filter(status=AMRRecord.Status.REVIEWED).count(),
        "closed": AMRRecord.objects.filter(status=AMRRecord.Status.CLOSED).count(),
        "high_risk": AMRRecord.objects.filter(
            risk_level=AMRRecord.RiskLevel.HIGH
        ).count(),
        "urgent": AMRRecord.objects.filter(
            risk_level=AMRRecord.RiskLevel.URGENT
        ).count(),
        "resistance_tests": ResistanceTest.objects.count(),
        "resistant_tests": ResistanceTest.objects.filter(
            result=ResistanceTest.Result.RESISTANT
        ).count(),
    }


def resistance_statistics():
    return {
        "susceptible": ResistanceTest.objects.filter(
            result=ResistanceTest.Result.SUSCEPTIBLE
        ).count(),
        "intermediate": ResistanceTest.objects.filter(
            result=ResistanceTest.Result.INTERMEDIATE
        ).count(),
        "resistant": ResistanceTest.objects.filter(
            result=ResistanceTest.Result.RESISTANT
        ).count(),
        "unknown": ResistanceTest.objects.filter(
            result=ResistanceTest.Result.UNKNOWN
        ).count(),
        "by_organism": list(
            ResistanceTest.objects.values("organism__name")
            .annotate(total=Count("id"))
            .order_by("organism__name")
        ),
        "by_antibiotic": list(
            ResistanceTest.objects.values("antibiotic__name")
            .annotate(total=Count("id"))
            .order_by("antibiotic__name")
        ),
    }


def referral_statistics():
    return {
        "total": Referral.objects.count(),
        "pending": Referral.objects.filter(status=Referral.Status.PENDING).count(),
        "sent": Referral.objects.filter(status=Referral.Status.SENT).count(),
        "accepted": Referral.objects.filter(status=Referral.Status.ACCEPTED).count(),
        "declined": Referral.objects.filter(status=Referral.Status.DECLINED).count(),
        "in_progress": Referral.objects.filter(
            status=Referral.Status.IN_PROGRESS
        ).count(),
        "completed": Referral.objects.filter(status=Referral.Status.COMPLETED).count(),
        "cancelled": Referral.objects.filter(status=Referral.Status.CANCELLED).count(),
        "emergency": Referral.objects.filter(
            priority=Referral.Priority.EMERGENCY
        ).count(),
        "urgent": Referral.objects.filter(priority=Referral.Priority.URGENT).count(),
    }


def facility_statistics():
    return {
        "total": Facility.objects.count(),
        "active": Facility.objects.filter(
            operating_status=Facility.OperatingStatus.ACTIVE
        ).count(),
        "inactive": Facility.objects.filter(
            operating_status=Facility.OperatingStatus.INACTIVE
        ).count(),
        "temporarily_closed": Facility.objects.filter(
            operating_status=Facility.OperatingStatus.TEMPORARILY_CLOSED
        ).count(),
        "referral_available": Facility.objects.filter(referral_available=True).count(),
    }


def follow_up_statistics():
    return {
        "total": FollowUp.objects.count(),
        "pending": FollowUp.objects.filter(status=FollowUp.Status.PENDING).count(),
        "completed": FollowUp.objects.filter(status=FollowUp.Status.COMPLETED).count(),
        "missed": FollowUp.objects.filter(status=FollowUp.Status.MISSED).count(),
        "rescheduled": FollowUp.objects.filter(
            status=FollowUp.Status.RESCHEDULED
        ).count(),
    }
