(function () {
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);
    const amrRecordId = params.get("amr_record_id");
    const patientId = params.get("patient_id");

    function getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const cookie of cookies) {
            const [key, ...value] = cookie.trim().split("=");

            if (key === name) {
                return decodeURIComponent(value.join("="));
            }
        }

        return "";
    }

    async function apiRequest(url, options = {}) {
        const requestOptions = {
            ...options,
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                ...(options.headers || {})
            }
        };

        const response = await fetch(url, requestOptions);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || "The request could not be completed.");
        }

        return data;
    }

    function showAlert(elementId, message, type = "danger") {
        const element = document.getElementById(elementId);

        if (!element) {
            return;
        }

        element.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
    }

    function clearAlert(elementId) {
        const element = document.getElementById(elementId);

        if (element) {
            element.innerHTML = "";
        }
    }

    function formatDate(value) {
        if (!value) {
            return "—";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString();
    }

    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
    }

    function getRiskClass(riskLevel) {
        if (riskLevel === "URGENT" || riskLevel === "HIGH") {
            return "text-danger fw-bold";
        }

        if (riskLevel === "MODERATE") {
            return "text-warning fw-bold";
        }

        if (riskLevel === "LOW") {
            return "text-success fw-bold";
        }

        return "";
    }

    function getStatusClass(status) {
        if (status === "OPEN") {
            return "text-danger fw-bold";
        }

        if (status === "UNDER_REVIEW") {
            return "text-warning fw-bold";
        }

        if (status === "REVIEWED" || status === "CLOSED") {
            return "text-success fw-bold";
        }

        return "";
    }

    function renderRecords(records) {
        const table = document.getElementById("amr-records");

        if (!table) {
            return;
        }

        if (!records.length) {
            table.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        No AMR records found.
                    </td>
                </tr>
            `;
            return;
        }

        table.innerHTML = records.map(record => `
            <tr>
                <td>${escapeHtml(record.patient_username)}</td>
                <td>${escapeHtml(record.screening_type)}</td>
                <td class="${getRiskClass(record.risk_level)}">
                    ${escapeHtml(record.risk_level_display || "Not specified")}
                </td>
                <td class="${getStatusClass(record.status)}">
                    ${escapeHtml(record.status_display || record.status)}
                </td>
                <td>${escapeHtml(formatDate(record.created_at))}</td>
                <td>
                    <a href="?amr_record_id=${record.id}" class="btn btn-sm btn-primary">
                        View
                    </a>
                </td>
            </tr>
        `).join("");
    }

    function updateDashboardStats(records) {
        const total = records.length;
        const open = records.filter(record => record.status === "OPEN").length;
        const review = records.filter(record => record.status === "UNDER_REVIEW").length;
        const highRisk = records.filter(record => ["HIGH", "URGENT"].includes(record.risk_level)).length;

        const totalElement = document.getElementById("total-records");
        const openElement = document.getElementById("open-records");
        const reviewElement = document.getElementById("review-records");
        const highRiskElement = document.getElementById("high-risk-records");

        if (totalElement) {
            totalElement.textContent = total;
        }

        if (openElement) {
            openElement.textContent = open;
        }

        if (reviewElement) {
            reviewElement.textContent = review;
        }

        if (highRiskElement) {
            highRiskElement.textContent = highRisk;
        }
    }

    async function loadPatientRecords() {
        const table = document.getElementById("amr-records");

        if (!table || !patientId) {
            return;
        }

        try {
            clearAlert("dashboard-alert");

            const data = await apiRequest(`/amr/patients/${patientId}/records/`);
            const records = data.records || [];

            renderRecords(records);
            updateDashboardStats(records);
        } catch (error) {
            showAlert("dashboard-alert", error.message);
        }
    }

    async function loadAmrRecord() {
        if (!amrRecordId) {
            return null;
        }

        try {
            const record = await apiRequest(`/amr/records/${amrRecordId}/`);
            displayAmrRecord(record);
            return record;
        } catch (error) {
            showAlert("assessment-alert", error.message);
            showAlert("result-alert", error.message);
            return null;
        }
    }

    function displayAmrRecord(record) {
        const patientName = document.getElementById("patient-name");
        const screeningType = document.getElementById("screening-type");

        if (patientName) {
            patientName.value = record.patient_username || "";
        }

        if (screeningType) {
            screeningType.value = record.screening_type || "";
        }

        const exposure = document.getElementById("exposure-history");
        const infection = document.getElementById("infection-information");
        const risk = document.getElementById("risk-level");
        const notes = document.getElementById("clinical-notes");

        if (exposure) {
            exposure.value = record.exposure_history || "";
        }

        if (infection) {
            infection.value = record.infection_information || "";
        }

        if (risk) {
            risk.value = record.risk_level || "";
        }

        if (notes) {
            notes.value = record.clinical_notes || "";
        }

        const resultPatient = document.getElementById("result-patient");
        const resultRisk = document.getElementById("result-risk");
        const resultStatus = document.getElementById("result-status");
        const resultScreening = document.getElementById("result-screening");
        const resultExposure = document.getElementById("result-exposure");
        const resultInfection = document.getElementById("result-infection");
        const resultNotes = document.getElementById("result-notes");

        if (resultPatient) {
            resultPatient.textContent = record.patient_username || "—";
        }

        if (resultRisk) {
            resultRisk.textContent = record.risk_level_display || "Not specified";
        }

        if (resultStatus) {
            resultStatus.textContent = record.status_display || record.status || "—";
        }

        if (resultScreening) {
            resultScreening.textContent = record.screening_type || "—";
        }

        if (resultExposure) {
            resultExposure.textContent = record.exposure_history || "No information available.";
        }

        if (resultInfection) {
            resultInfection.textContent = record.infection_information || "No information available.";
        }

        if (resultNotes) {
            resultNotes.textContent = record.clinical_notes || "No clinical notes available.";
        }

        renderResistanceTests(record.resistance_tests || []);
    }

    function renderResistanceTests(tests) {
        const assessmentTable = document.getElementById("resistance-tests");
        const resultTable = document.getElementById("result-resistance-tests");

        const html = tests.length
            ? tests.map(test => `
                <tr>
                    <td>${escapeHtml(test.organism_name)}</td>
                    <td>${escapeHtml(test.antibiotic_name)}</td>
                    <td class="${test.result === "RESISTANT" ? "text-danger fw-bold" : ""}">
                        ${escapeHtml(test.result_display || test.result)}
                    </td>
                    <td>${escapeHtml(test.test_notes || "—")}</td>
                    <td>${escapeHtml(formatDate(test.tested_at))}</td>
                </tr>
            `).join("")
            : `
                <tr>
                    <td colspan="5" class="text-center">
                        No resistance tests recorded.
                    </td>
                </tr>
            `;

        if (assessmentTable) {
            assessmentTable.innerHTML = html;
        }

        if (resultTable) {
            resultTable.innerHTML = html;
        }
    }

    function setupResistanceTestForm() {
        const form = document.getElementById("resistance-test-form");

        if (!form || !amrRecordId) {
            return;
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const formData = new FormData();

            formData.append("organism_id", document.getElementById("organism").value);
            formData.append("antibiotic_id", document.getElementById("antibiotic").value);
            formData.append("result", document.getElementById("result").value);
            formData.append("test_notes", document.getElementById("test-notes").value);

            try {
                const test = await apiRequest(`/amr/records/${amrRecordId}/resistance-tests/`, {
                    method: "POST",
                    body: formData
                });

                showAlert("assessment-alert", "Resistance test added successfully.", "success");

                form.reset();

                const record = await apiRequest(`/amr/records/${amrRecordId}/`);
                renderResistanceTests(record.resistance_tests || []);
            } catch (error) {
                showAlert("assessment-alert", error.message);
            }
        });
    }

    function calculateSurveillance(records) {
        const tests = records.flatMap(record => record.resistance_tests || []);

        const resistant = tests.filter(test => test.result === "RESISTANT").length;
        const highRisk = records.filter(record => ["HIGH", "URGENT"].includes(record.risk_level)).length;

        return {
            records,
            tests,
            resistant,
            highRisk
        };
    }

    function renderSurveillance(data) {
        const table = document.getElementById("surveillance-data");

        if (!table) {
            return;
        }

        if (!data.tests.length) {
            table.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        No surveillance data available.
                    </td>
                </tr>
            `;
            return;
        }

        table.innerHTML = data.records.flatMap(record =>
            (record.resistance_tests || []).map(test => `
                <tr>
                    <td>${escapeHtml(record.patient_username)}</td>
                    <td>${escapeHtml(test.organism_name)}</td>
                    <td>${escapeHtml(test.antibiotic_name)}</td>
                    <td class="${test.result === "RESISTANT" ? "text-danger fw-bold" : ""}">
                        ${escapeHtml(test.result_display || test.result)}
                    </td>
                    <td class="${getRiskClass(record.risk_level)}">
                        ${escapeHtml(record.risk_level_display || "Not specified")}
                    </td>
                    <td class="${getStatusClass(record.status)}">
                        ${escapeHtml(record.status_display || record.status)}
                    </td>
                </tr>
            `)
        ).join("");
    }

    function updateSurveillanceStats(data) {
        const recordsElement = document.getElementById("surveillance-records");
        const testsElement = document.getElementById("surveillance-tests");
        const resistantElement = document.getElementById("resistant-findings");
        const highRiskElement = document.getElementById("surveillance-high-risk");

        if (recordsElement) {
            recordsElement.textContent = data.records.length;
        }

        if (testsElement) {
            testsElement.textContent = data.tests.length;
        }

        if (resistantElement) {
            resistantElement.textContent = data.resistant;
        }

        if (highRiskElement) {
            highRiskElement.textContent = data.highRisk;
        }

        const summary = document.getElementById("surveillance-summary");

        if (summary) {
            summary.innerHTML = `
                <p>
                    ${data.records.length} AMR record(s), ${data.tests.length}
                    resistance test(s), and ${data.resistant} resistant finding(s)
                    are currently available.
                </p>
            `;
        }
    }

    async function loadSurveillance() {
        const table = document.getElementById("surveillance-data");

        if (!table || !patientId) {
            return;
        }

        try {
            clearAlert("surveillance-alert");

            const response = await apiRequest(`/amr/patients/${patientId}/records/`);
            const data = calculateSurveillance(response.records || []);

            renderSurveillance(data);
            updateSurveillanceStats(data);
        } catch (error) {
            showAlert("surveillance-alert", error.message);
        }
    }

    function setupNavigation() {
        const dashboardLinks = [
            "back-dashboard",
            "result-dashboard",
            "surveillance-dashboard"
        ];

        dashboardLinks.forEach(id => {
            const element = document.getElementById(id);

            if (element) {
                element.href = "/amr/dashboard/";
            }
        });

        const assessmentLinks = [
            "assessment-link",
            "open-assessment"
        ];

        assessmentLinks.forEach(id => {
            const element = document.getElementById(id);

            if (element && amrRecordId) {
                element.href = `/amr/assessment/?amr_record_id=${amrRecordId}`;
            }
        });

        const surveillanceLinks = [
            "surveillance-link",
            "open-surveillance"
        ];

        surveillanceLinks.forEach(id => {
            const element = document.getElementById(id);

            if (element && patientId) {
                element.href = `/amr/surveillance/?patient_id=${patientId}`;
            }
        });
    }

    function setupRefreshButtons() {
        const refreshRecords = document.getElementById("refresh-records");

        if (refreshRecords) {
            refreshRecords.addEventListener("click", loadPatientRecords);
        }

        const refreshSurveillance = document.getElementById("refresh-surveillance");

        if (refreshSurveillance) {
            refreshSurveillance.addEventListener("click", loadSurveillance);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        setupNavigation();
        setupRefreshButtons();
        setupResistanceTestForm();

        if (document.getElementById("amr-records")) {
            loadPatientRecords();
        }

        if (document.getElementById("patient-name") || document.getElementById("result-patient")) {
            loadAmrRecord();
        }

        if (document.getElementById("surveillance-data")) {
            loadSurveillance();
        }
    });
})();