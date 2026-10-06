document.addEventListener("DOMContentLoaded", () => {
    const messageBox = document.getElementById("followUpMessage");

    function showMessage(message, type = "success") {
        if (!messageBox) {
            return;
        }

        messageBox.className = `alert alert-${type}`;
        messageBox.textContent = message;
        messageBox.classList.remove("d-none");

        window.setTimeout(() => {
            messageBox.classList.add("d-none");
        }, 5000);
    }


    function getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const cookie of cookies) {
            const trimmedCookie = cookie.trim();

            if (trimmedCookie.startsWith(`${name}=`)) {
                return decodeURIComponent(
                    trimmedCookie.substring(name.length + 1)
                );
            }
        }

        return null;
    }


    function getCSRFToken() {
        return getCookie("csrftoken");
    }


    async function apiRequest(url, options = {}) {
        const requestOptions = {
            ...options,
            headers: {
                ...(options.headers || {}),
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
        };

        const response = await fetch(url, requestOptions);

        let data;

        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || data.success === false) {
            throw new Error(
                data.error ||
                data.message ||
                "The requested operation failed."
            );
        }

        return data;
    }


    function updateStatistics(followUps) {
        const totalElement = document.getElementById("totalFollowUps");
        const pendingElement = document.getElementById("pendingFollowUps");
        const completedElement = document.getElementById("completedFollowUps");
        const missedElement = document.getElementById("missedFollowUps");

        if (totalElement) {
            totalElement.textContent = followUps.length;
        }

        if (pendingElement) {
            pendingElement.textContent = followUps.filter(
                item => item.status === "PENDING"
            ).length;
        }

        if (completedElement) {
            completedElement.textContent = followUps.filter(
                item => item.status === "COMPLETED"
            ).length;
        }

        if (missedElement) {
            missedElement.textContent = followUps.filter(
                item => item.status === "MISSED"
            ).length;
        }
    }


    function formatDateTime(value) {
        if (!value) {
            return "—";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString([], {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }


    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    }


    function renderFollowUps(followUps) {
        const tableBody = document.getElementById("followUpTableBody");

        if (!tableBody) {
            return;
        }

        tableBody.innerHTML = "";

        if (!followUps.length) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-5">
                        <div class="text-secondary">
                            No follow-ups have been recorded yet.
                        </div>

                        <a
                            href="/followups/create/"
                            class="btn btn-primary btn-sm mt-3"
                        >
                            Create First Follow-up
                        </a>
                    </td>
                </tr>
            `;

            return;
        }

        followUps.forEach(followUp => {
            const row = document.createElement("tr");

            const patientName = escapeHtml(
                followUp.patient_name || "Unknown patient"
            );

            const typeName = escapeHtml(
                followUp.follow_up_type_display ||
                followUp.follow_up_type ||
                "—"
            );

            const reason = escapeHtml(
                followUp.reason || "—"
            );

            const statusName = escapeHtml(
                followUp.status_display ||
                followUp.status ||
                "—"
            );

            const statusClass = String(
                followUp.status || ""
            ).toLowerCase();

            row.innerHTML = `
                <td>
                    <div class="fw-semibold">
                        ${patientName}
                    </div>
                </td>

                <td>
                    ${typeName}
                </td>

                <td>
                    <span class="text-secondary">
                        ${reason.length > 70
                            ? `${reason.substring(0, 70)}...`
                            : reason}
                    </span>
                </td>

                <td>
                    ${escapeHtml(
                        formatDateTime(followUp.scheduled_at)
                    )}
                </td>

                <td>
                    <span
                        class="badge followup-status-badge status-${statusClass}"
                    >
                        ${statusName}
                    </span>
                </td>

                <td class="text-end">
                    <a
                        href="/followups/detail/${followUp.id}/"
                        class="btn btn-outline-primary btn-sm"
                    >
                        View
                    </a>
                </td>
            `;

            tableBody.appendChild(row);
        });
    }


    async function loadFollowUps() {
        const tableBody = document.getElementById("followUpTableBody");

        try {
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-5">
                            <div class="spinner-border spinner-border-sm me-2"></div>
                            Loading follow-ups...
                        </td>
                    </tr>
                `;
            }

            const data = await apiRequest(
                "/followups/api/records/"
            );

            const followUps = data.follow_ups || [];

            updateStatistics(followUps);
            renderFollowUps(followUps);

        } catch (error) {
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td
                            colspan="6"
                            class="text-center text-danger py-5"
                        >
                            ${escapeHtml(error.message)}
                        </td>
                    </tr>
                `;
            }

            showMessage(
                error.message,
                "danger"
            );
        }
    }


    function filterReferralsByPatient() {
        const patientSelect = document.getElementById("patient");
        const referralSelect = document.getElementById("referral");

        if (!patientSelect || !referralSelect) {
            return;
        }

        const selectedPatient = patientSelect.value;

        Array.from(referralSelect.options).forEach(option => {
            if (!option.value) {
                option.hidden = false;
                return;
            }

            const referralPatient = option.dataset.patient;

            option.hidden =
                selectedPatient &&
                referralPatient !== selectedPatient;
        });

        if (
            referralSelect.value &&
            referralSelect.selectedOptions[0]?.hidden
        ) {
            referralSelect.value = "";
        }
    }


    function validateCompletedFields() {
        const statusSelect = document.getElementById("status");
        const completedAt = document.getElementById("completed_at");
        const outcome = document.getElementById("outcome");

        if (!statusSelect) {
            return true;
        }

        if (
            statusSelect.value === "COMPLETED" &&
            completedAt &&
            !completedAt.value
        ) {
            showMessage(
                "Completed date and time is required when the status is completed.",
                "warning"
            );

            completedAt.focus();

            return false;
        }

        if (
            statusSelect.value === "COMPLETED" &&
            outcome &&
            !outcome.value.trim()
        ) {
            showMessage(
                "Please enter the follow-up outcome before marking it as completed.",
                "warning"
            );

            outcome.focus();

            return false;
        }

        return true;
    }


    async function createFollowUp() {
        const form = document.getElementById("createFollowUpForm");

        if (!form) {
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        if (!validateCompletedFields()) {
            return;
        }

        const button = document.getElementById(
            "createFollowUpButton"
        );

        const formData = new FormData(form);

        if (button) {
            button.disabled = true;
            button.textContent = "Creating...";
        }

        try {
            const data = await apiRequest(
                "/followups/api/create/",
                {
                    method: "POST",
                    body: formData,
                }
            );

            showMessage(
                data.message || "Follow-up created successfully.",
                "success"
            );

            form.reset();

            const referralSelect =
                document.getElementById("referral");

            if (referralSelect) {
                referralSelect.value = "";
            }

            window.setTimeout(() => {
                window.location.href =
                    `/followups/detail/${data.follow_up.id}/`;
            }, 700);

        } catch (error) {
            showMessage(
                error.message,
                "danger"
            );

        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Create Follow-up";
            }
        }
    }


    async function completeFollowUp() {
        const button = document.getElementById(
            "completeFollowUpButton"
        );

        if (!button) {
            return;
        }

        const followUpId = button.dataset.followUpId;

        const confirmed = window.confirm(
            "Are you sure you want to mark this follow-up as completed?"
        );

        if (!confirmed) {
            return;
        }

        button.disabled = true;
        button.textContent = "Completing...";

        try {
            const outcome = window.prompt(
                "Enter the follow-up outcome:",
                ""
            );

            if (outcome === null) {
                button.disabled = false;
                button.textContent = "Mark as Completed";
                return;
            }

            const notes = window.prompt(
                "Enter any additional notes:",
                ""
            );

            if (notes === null) {
                button.disabled = false;
                button.textContent = "Mark as Completed";
                return;
            }

            const formData = new FormData();

            formData.append(
                "outcome",
                outcome
            );

            formData.append(
                "notes",
                notes
            );

            const data = await apiRequest(
                `/followups/api/records/${followUpId}/complete/`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            showMessage(
                data.message ||
                "Follow-up completed successfully.",
                "success"
            );

            window.setTimeout(() => {
                window.location.reload();
            }, 700);

        } catch (error) {
            showMessage(
                error.message,
                "danger"
            );

            button.disabled = false;
            button.textContent = "Mark as Completed";
        }
    }


    async function rescheduleFollowUp() {
        const button = document.getElementById(
            "rescheduleFollowUpButton"
        );

        if (!button) {
            return;
        }

        const followUpId = button.dataset.followUpId;

        const scheduledAt = window.prompt(
            "Enter the new scheduled date and time.\n\nFormat: YYYY-MM-DDTHH:mm",
            ""
        );

        if (!scheduledAt) {
            return;
        }

        const notes = window.prompt(
            "Enter rescheduling notes:",
            ""
        );

        if (notes === null) {
            return;
        }

        button.disabled = true;
        button.textContent = "Rescheduling...";

        try {
            const formData = new FormData();

            formData.append(
                "scheduled_at",
                scheduledAt
            );

            formData.append(
                "notes",
                notes
            );

            const data = await apiRequest(
                `/followups/api/records/${followUpId}/reschedule/`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            showMessage(
                data.message ||
                "Follow-up rescheduled successfully.",
                "success"
            );

            window.setTimeout(() => {
                window.location.reload();
            }, 700);

        } catch (error) {
            showMessage(
                error.message,
                "danger"
            );

            button.disabled = false;
            button.textContent = "Reschedule";
        }
    }


    async function editFollowUp() {
        const button = document.getElementById(
            "editFollowUpButton"
        );

        if (!button) {
            return;
        }

        const followUpId = button.dataset.followUpId;

        const reason = window.prompt(
            "Enter the updated follow-up reason:"
        );

        if (reason === null) {
            return;
        }

        if (!reason.trim()) {
            showMessage(
                "Follow-up reason is required.",
                "warning"
            );

            return;
        }

        const scheduledAt = window.prompt(
            "Enter the updated scheduled date and time.\n\nFormat: YYYY-MM-DDTHH:mm",
            ""
        );

        if (!scheduledAt) {
            return;
        }

        const status = window.prompt(
            "Enter the status:\nPENDING, COMPLETED, MISSED, or RESCHEDULED",
            "PENDING"
        );

        if (!status) {
            return;
        }

        const outcome = window.prompt(
            "Enter the outcome:",
            ""
        );

        if (outcome === null) {
            return;
        }

        const notes = window.prompt(
            "Enter the notes:",
            ""
        );

        if (notes === null) {
            return;
        }

        button.disabled = true;
        button.textContent = "Updating...";

        try {
            const formData = new FormData();

            formData.append(
                "reason",
                reason.trim()
            );

            formData.append(
                "scheduled_at",
                scheduledAt
            );

            formData.append(
                "status",
                status.trim().toUpperCase()
            );

            formData.append(
                "outcome",
                outcome.trim()
            );

            formData.append(
                "notes",
                notes.trim()
            );

            const data = await apiRequest(
                `/followups/api/records/${followUpId}/update/`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            showMessage(
                data.message ||
                "Follow-up updated successfully.",
                "success"
            );

            window.setTimeout(() => {
                window.location.reload();
            }, 700);

        } catch (error) {
            showMessage(
                error.message,
                "danger"
            );

            button.disabled = false;
            button.textContent = "Edit Follow-up";
        }
    }


    const refreshButton = document.getElementById(
        "refreshFollowUps"
    );

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            loadFollowUps
        );
    }


    const patientSelect = document.getElementById(
        "patient"
    );

    if (patientSelect) {
        patientSelect.addEventListener(
            "change",
            filterReferralsByPatient
        );

        filterReferralsByPatient();
    }


    const createForm = document.getElementById(
        "createFollowUpForm"
    );

    if (createForm) {
        createForm.addEventListener(
            "submit",
            event => {
                event.preventDefault();
                createFollowUp();
            }
        );
    }


    const completeButton = document.getElementById(
        "completeFollowUpButton"
    );

    if (completeButton) {
        completeButton.addEventListener(
            "click",
            completeFollowUp
        );
    }


    const rescheduleButton = document.getElementById(
        "rescheduleFollowUpButton"
    );

    if (rescheduleButton) {
        rescheduleButton.addEventListener(
            "click",
            rescheduleFollowUp
        );
    }


    const editButton = document.getElementById(
        "editFollowUpButton"
    );

    if (editButton) {
        editButton.addEventListener(
            "click",
            editFollowUp
        );
    }


    const followUpTableBody = document.getElementById(
        "followUpTableBody"
    );

    if (followUpTableBody) {
        loadFollowUps();
    }
});