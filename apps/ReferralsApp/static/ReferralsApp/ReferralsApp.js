document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    if (path.includes("/referrals/create/")) {
        initializeCreateReferral();
    }

    if (path.includes("/referrals/list/")) {
        initializeReferralList();
    }

    if (path.includes("/referrals/detail/")) {
        initializeReferralDetail();
    }

    if (path.includes("/referrals/tracking/")) {
        initializeReferralTracking();
    }
});


function getCsrfToken() {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}


async function request(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest",
            ...(options.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}


function showMessage(message, type = "info") {
    const container = document.querySelector("#referral-message");

    if (!container) {
        alert(message);
        return;
    }

    container.className = `alert alert-${type}`;
    container.textContent = message;
    container.classList.remove("d-none");
}


function hideMessage() {
    const container = document.querySelector("#referral-message");

    if (container) {
        container.classList.add("d-none");
    }
}


async function initializeCreateReferral() {
    const form = document.querySelector("#referral-create-form");

    if (!form) {
        return;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        hideMessage();

        const formData = new FormData(form);

        try {
            const referral = await request("/referrals/api/create/", {
                method: "POST",
                body: formData
            });

            showMessage(
                `Referral #${referral.id} created successfully.`,
                "success"
            );

            form.reset();

            setTimeout(() => {
                window.location.href =
                    `/referrals/detail/${referral.id}/`;
            }, 800);
        } catch (error) {
            showMessage(error.message, "danger");
        }
    });
}


async function initializeReferralList() {
    const container = document.querySelector("#referrals-container");

    if (!container) {
        return;
    }

    try {
        const data = await request("/referrals/api/records/");

        renderReferralList(container, data.referrals || []);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


function renderReferralList(container, referrals) {
    if (!referrals.length) {
        container.innerHTML = `
            <div class="alert alert-secondary">
                No referrals found.
            </div>
        `;
        return;
    }

    container.innerHTML = referrals.map(referral => `
        <div class="card mb-3 referral-card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">
                            Referral #${referral.id}
                        </h5>

                        <p class="mb-1">
                            <strong>Patient:</strong>
                            ${escapeHtml(referral.patient_username || "Unknown")}
                        </p>

                        <p class="mb-1">
                            <strong>Reason:</strong>
                            ${escapeHtml(referral.referral_reason)}
                        </p>

                        <p class="mb-1">
                            <strong>Destination:</strong>
                            ${escapeHtml(referral.destination_name || "Not specified")}
                        </p>
                    </div>

                    <span class="badge bg-secondary">
                        ${escapeHtml(referral.status_display)}
                    </span>
                </div>

                <div class="mt-3">
                    <span class="badge bg-primary">
                        ${escapeHtml(referral.priority_display)}
                    </span>

                    <a
                        href="/referrals/detail/${referral.id}/"
                        class="btn btn-sm btn-outline-primary ms-2"
                    >
                        View Details
                    </a>
                </div>
            </div>
        </div>
    `).join("");
}


async function initializeReferralDetail() {
    const container = document.querySelector("#referral-detail");

    if (!container) {
        return;
    }

    const referralId = container.dataset.referralId;

    if (!referralId) {
        container.innerHTML = `
            <div class="alert alert-danger">
                Referral ID is missing.
            </div>
        `;
        return;
    }

    try {
        const referral = await request(
            `/referrals/api/records/${referralId}/`
        );

        renderReferralDetail(container, referral);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


function renderReferralDetail(container, referral) {
    container.innerHTML = `
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <h3>Referral #${referral.id}</h3>

                    <span class="badge bg-secondary">
                        ${escapeHtml(referral.status_display)}
                    </span>
                </div>

                <hr>

                <p>
                    <strong>Patient:</strong>
                    ${escapeHtml(referral.patient_username || "Unknown")}
                </p>

                <p>
                    <strong>Reason:</strong>
                    ${escapeHtml(referral.referral_reason)}
                </p>

                <p>
                    <strong>Clinical Summary:</strong>
                    ${escapeHtml(referral.clinical_summary || "Not provided")}
                </p>

                <p>
                    <strong>Destination:</strong>
                    ${escapeHtml(referral.destination_name || "Not specified")}
                </p>

                <p>
                    <strong>Priority:</strong>
                    ${escapeHtml(referral.priority_display)}
                </p>

                <p>
                    <strong>AMR Risk:</strong>
                    ${escapeHtml(referral.amr_risk_level || "Not available")}
                </p>

                <p>
                    <strong>Notes:</strong>
                    ${escapeHtml(referral.referral_notes || "None")}
                </p>

                <hr>

                <div class="row g-2">
                    <div class="col-md-6">
                        <label for="referral-status" class="form-label">
                            Update Status
                        </label>

                        <select
                            id="referral-status"
                            class="form-select"
                        >
                            ${renderStatusOptions(referral.status)}
                        </select>
                    </div>

                    <div class="col-md-6 d-flex align-items-end">
                        <button
                            type="button"
                            id="update-referral-status"
                            class="btn btn-primary"
                        >
                            Update Status
                        </button>
                    </div>
                </div>

                <div
                    id="referral-message"
                    class="alert d-none mt-3"
                ></div>
            </div>
        </div>
    `;

    const button = document.querySelector("#update-referral-status");

    button.addEventListener("click", async () => {
        const status = document.querySelector("#referral-status").value;

        const formData = new FormData();
        formData.append("status", status);

        try {
            const updated = await request(
                `/referrals/api/records/${referral.id}/status/`,
                {
                    method: "POST",
                    body: formData
                }
            );

            showMessage("Referral status updated successfully.", "success");

            const statusBadge = container.querySelector(".badge");

            if (statusBadge) {
                statusBadge.textContent = updated.status_display;
            }
        } catch (error) {
            showMessage(error.message, "danger");
        }
    });
}


function renderStatusOptions(currentStatus) {
    const statuses = [
        ["PENDING", "Pending"],
        ["SENT", "Sent"],
        ["ACCEPTED", "Accepted"],
        ["DECLINED", "Declined"],
        ["IN_PROGRESS", "In Progress"],
        ["COMPLETED", "Completed"],
        ["CANCELLED", "Cancelled"]
    ];

    return statuses.map(([value, label]) => `
        <option
            value="${value}"
            ${value === currentStatus ? "selected" : ""}
        >
            ${label}
        </option>
    `).join("");
}


async function initializeReferralTracking() {
    const container = document.querySelector("#tracking-container");

    if (!container) {
        return;
    }

    try {
        const data = await request("/referrals/api/records/");

        renderReferralTracking(container, data.referrals || []);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


function renderReferralTracking(container, referrals) {
    if (!referrals.length) {
        container.innerHTML = `
            <div class="alert alert-secondary">
                No referrals available for tracking.
            </div>
        `;
        return;
    }

    container.innerHTML = referrals.map(referral => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h5>
                            Referral #${referral.id}
                        </h5>

                        <p class="mb-1">
                            ${escapeHtml(referral.referral_reason)}
                        </p>

                        <small class="text-muted">
                            ${escapeHtml(
                                referral.destination_name || "Destination not specified"
                            )}
                        </small>
                    </div>

                    <span class="badge bg-primary">
                        ${escapeHtml(referral.status_display)}
                    </span>
                </div>

                <div class="progress mt-3" style="height: 8px;">
                    <div
                        class="progress-bar"
                        role="progressbar"
                        style="width: ${getProgress(referral.status)}%"
                    ></div>
                </div>
            </div>
        </div>
    `).join("");
}


function getProgress(status) {
    const progress = {
        PENDING: 15,
        SENT: 30,
        ACCEPTED: 50,
        DECLINED: 100,
        IN_PROGRESS: 70,
        COMPLETED: 100,
        CANCELLED: 100
    };

    return progress[status] || 0;
}


function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}