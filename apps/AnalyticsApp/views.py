from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.AnalyticsApp.serializers import (
    DashboardStatisticsSerializer,
    AMRStatisticsSerializer,
    FacilityStatisticsSerializer,
    FollowUpStatisticsSerializer,
    ReferralStatisticsSerializer,
    ScreeningStatisticsSerializer,
)
from apps.AnalyticsApp.services import (
    get_amr_analytics,
    get_dashboard_statistics,
    get_facility_analytics,
    get_follow_up_analytics,
    get_referral_analytics,
    get_screening_analytics,
)


def analytics_access_allowed(user):
    return user.is_authenticated and user.role in {
        "CLINICIAN",
        "FACILITY_STAFF",
        "ADMIN",
    }


@login_required
def dashboard_page(request):
    if not analytics_access_allowed(request.user):
        return JsonResponse(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    return render(
        request,
        "AnalyticsApp/dashboard.html",
    )


@login_required
def screening_page(request):
    if not analytics_access_allowed(request.user):
        return JsonResponse(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    return render(
        request,
        "AnalyticsApp/screening.html",
    )


@login_required
def amr_page(request):
    if not analytics_access_allowed(request.user):
        return JsonResponse(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    return render(
        request,
        "AnalyticsApp/amr.html",
    )


@login_required
def referrals_page(request):
    if not analytics_access_allowed(request.user):
        return JsonResponse(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    return render(
        request,
        "AnalyticsApp/referrals.html",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_dashboard_statistics()
    serializer = DashboardStatisticsSerializer(data)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def screening_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_screening_analytics()

    return Response(
        {
            "screening": ScreeningStatisticsSerializer(data["screening"]).data,
            "risk": data["risk"],
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def amr_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_amr_analytics()

    return Response(
        {
            "amr": AMRStatisticsSerializer(data["amr"]).data,
            "resistance": data["resistance"],
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def referrals_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_referral_analytics()

    return Response(ReferralStatisticsSerializer(data["referrals"]).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def facilities_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_facility_analytics()

    return Response(FacilityStatisticsSerializer(data["facilities"]).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def follow_ups_api(request):
    if not analytics_access_allowed(request.user):
        return Response(
            {"detail": "You do not have permission to access analytics."},
            status=403,
        )

    data = get_follow_up_analytics()

    return Response(FollowUpStatisticsSerializer(data["follow_ups"]).data)
