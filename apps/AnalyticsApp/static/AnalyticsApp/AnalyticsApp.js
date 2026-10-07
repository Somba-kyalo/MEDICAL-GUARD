document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    if (path.endsWith("/analytics/") || path.endsWith("/analytics/dashboard/")) {
        loadDashboardAnalytics();
        return;
    }

    if (path.endsWith("/analytics/screening/")) {
        loadScreeningAnalytics();
        return;
    }

    if (path.endsWith("/analytics/amr/")) {
        loadAMRAnalytics();
        return;
    }

    if (path.endsWith("/analytics/referrals/")) {
        loadReferralAnalytics();
    }
});

async function fetchAnalytics(url) {
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
    });

    if (!response.ok) {
        throw new Error(`Analytics request failed: ${response.status}`);
    }

    return response.json();
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? 0;
    }
}

function showAnalyticsError(message) {
    const errorElement = document.getElementById("analyticsError");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = message;
    errorElement.classList.remove("d-none");
}

function hideAnalyticsError() {
    const errorElement = document.getElementById("analyticsError");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = "";
    errorElement.classList.add("d-none");
}

async function loadDashboardAnalytics() {
    try {
        hideAnalyticsError();

        const data = await fetchAnalytics("/analytics/api/dashboard/");

        setText("totalPatients", data.patients.total);
        setText("totalScreenings", data.screening.total);
        setText("totalAmrRecords", data.amr.records);
        setText("totalReferrals", data.referrals.total);

        setText("completedScreenings", data.screening.completed);
        setText("progressScreenings", data.screening.in_progress);
        setText("reviewScreenings", data.screening.under_review);
        setText("reviewedScreenings", data.screening.reviewed);

        setText("pendingFollowUps", data.follow_ups.pending);
        setText("completedFollowUps", data.follow_ups.completed);
        setText("missedFollowUps", data.follow_ups.missed);
        setText("rescheduledFollowUps", data.follow_ups.rescheduled);
    } catch (error) {
        console.error("Dashboard analytics error:", error);
        showAnalyticsError("Unable to load dashboard analytics.");
    }
}

async function loadScreeningAnalytics() {
    try {
        hideAnalyticsError();

        const data = await fetchAnalytics("/analytics/api/screening/");

        setText("screeningTotal", data.screening.total);
        setText("screeningCompleted", data.screening.completed);
        setText("screeningInProgress", data.screening.in_progress);
        setText("screeningUnderReview", data.screening.under_review);
        setText("screeningReviewed", data.screening.reviewed);

        setText("riskLow", data.risk.low);
        setText("riskModerate", data.risk.moderate);
        setText("riskHigh", data.risk.high);
        setText("riskUrgent", data.risk.urgent);

        renderScreeningTypes(data.screening.by_type);
    } catch (error) {
        console.error("Screening analytics error:", error);
        showAnalyticsError("Unable to load screening analytics.");
    }
}

function renderScreeningTypes(screeningTypes) {
    const container = document.getElementById("screeningTypes");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!screeningTypes || screeningTypes.length === 0) {
        container.innerHTML = `
            <div class="analytics-empty">
                No screening type data available.
            </div>
        `;
        return;
    }

    screeningTypes.forEach((item) => {
        const row = document.createElement("div");
        row.className = "d-flex justify-content-between align-items-center border-bottom py-2";

        const label = document.createElement("span");
        label.className = "analytics-list-label";
        label.textContent = item.screening_type || "Unknown";

        const value = document.createElement("strong");
        value.className = "analytics-list-value";
        value.textContent = item.count ?? 0;

        row.appendChild(label);
        row.appendChild(value);

        container.appendChild(row);
    });
}

async function loadAMRAnalytics() {
    try {
        hideAnalyticsError();

        const data = await fetchAnalytics("/analytics/api/amr/");

        setText("amrRecords", data.amr.records);
        setText("resistanceTests", data.amr.resistance_tests);
        setText("resistantTests", data.amr.resistant_tests);
        setText("urgentAmr", data.amr.urgent);

        setText("amrOpen", data.amr.open);
        setText("amrUnderReview", data.amr.under_review);
        setText("amrReviewed", data.amr.reviewed);
        setText("amrClosed", data.amr.closed);

        setText("susceptibleResults", data.resistance.susceptible);
        setText("intermediateResults", data.resistance.intermediate);
        setText("resistantResults", data.resistance.resistant);
        setText("unknownResults", data.resistance.unknown);
    } catch (error) {
        console.error("AMR analytics error:", error);
        showAnalyticsError("Unable to load AMR analytics.");
    }
}

async function loadReferralAnalytics() {
    try {
        hideAnalyticsError();

        const data = await fetchAnalytics("/analytics/api/referrals/");

        setText("referralTotal", data.total);
        setText("referralAccepted", data.accepted);
        setText("referralInProgress", data.in_progress);
        setText("referralCompleted", data.completed);

        setText("referralPending", data.pending);
        setText("referralSent", data.sent);
        setText("referralDeclined", data.declined);
        setText("referralCancelled", data.cancelled);

        setText("referralUrgent", data.urgent);
        setText("referralEmergency", data.emergency);
    } catch (error) {
        console.error("Referral analytics error:", error);
        showAnalyticsError("Unable to load referral analytics.");
    }
}