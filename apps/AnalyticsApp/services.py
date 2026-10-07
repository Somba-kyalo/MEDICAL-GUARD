from apps.AnalyticsApp.queries import (
    amr_statistics,
    facility_statistics,
    follow_up_statistics,
    patient_statistics,
    referral_statistics,
    resistance_statistics,
    screening_risk_statistics,
    screening_statistics,
)


def get_dashboard_statistics():
    return {
        "patients": patient_statistics(),
        "screening": screening_statistics(),
        "screening_risk": screening_risk_statistics(),
        "amr": amr_statistics(),
        "resistance": resistance_statistics(),
        "referrals": referral_statistics(),
        "facilities": facility_statistics(),
        "follow_ups": follow_up_statistics(),
    }


def get_screening_analytics():
    return {
        "screening": screening_statistics(),
        "risk": screening_risk_statistics(),
    }


def get_amr_analytics():
    return {
        "amr": amr_statistics(),
        "resistance": resistance_statistics(),
    }


def get_referral_analytics():
    return {
        "referrals": referral_statistics(),
    }


def get_facility_analytics():
    return {
        "facilities": facility_statistics(),
    }


def get_follow_up_analytics():
    return {
        "follow_ups": follow_up_statistics(),
    }
