(function () {
    const params = new URLSearchParams(window.location.search);
    const amrRecordId = params.get("amr_record_id");

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

        if (element) {
            element.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        }
    }

    function clearAlert(elementId) {
        const element = document.getElementById(elementId);

        if (element) {
            element.innerHTML = "";
        }
    }

    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = value ?? "";
        return element.innerHTML;
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

    function riskClass(risk) {
        if (risk === "HIGH" || risk === "URGENT") {
            return "text-danger fw-bold";
        }

        if (risk === "MODERATE") {
            return "text-warning fw-bold";
        }

        if (risk === "LOW") {
            return "text-success fw-bold";
        }

        return "";
    }

    function statusClass(status) {
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

    async function loadAllRecords() {
        try {
            clearAlert("dashboard-alert");

            const data = await apiRequest("/amr/records/");
            const records = data.records || [];

            renderDashboard(records);
            return records;
        } catch (error) {
            showAlert("dashboard-alert", error.message);
            return [];
        }
    }

    function renderDashboard(records) {
        const table = document.getElementById("amr-records");

        if (!table) {
            return;
        }

        const total = records.length;
        const open = records.filter(record => record.status === "OPEN").length;
        const review = records.filter(record => record.status === "UNDER_REVIEW").length;
        const highRisk = records.filter(record => ["HIGH", "URGENT"].includes(record.risk_level)).length;

        document.getElementById("total-records").textContent = total;
        document.getElementById("open-records").textContent = open;
        document.getElementById("review-records").textContent = review;
        document.getElementById("high-risk-records").textContent = highRisk;

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
                <td class="${riskClass(record.risk_level)}">
                    ${escapeHtml(record.risk_level_display || "Not specified")}
                </td>
                <td class="${statusClass(record.status)}">
                    ${escapeHtml(record.status_display || record.status)}
                </td>
                <td>${escapeHtml(formatDate(record.created_at))}</td>
                <td>
                    <a href="/amr/result/?amr_record_id=${record.id}" class="btn btn-sm btn-primary">
                        View
                    </a>
                </td>
            </tr>
        `).join("");
    }

    async function loadAmrRecord() {
        if (!amrRecordId) {
            showAlert("assessment-alert", "No AMR record was selected.");
            showAlert("result-alert", "No AMR record was selected.");
            return null;
        }

        try {
            const record = await apiRequest(`/amr/records/${amrRecordId}/`);
            populateRecord(record);
            return record;
        } catch (error) {
            showAlert("assessment-alert", error.message);
            showAlert("result-alert", error.message);
            return null;
        }
    }

    function populateRecord(record) {
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

    async function saveAssessment(event) {
        event.preventDefault();

        if (!amrRecordId) {
            showAlert("assessment-alert", "No AMR record was selected.");
            return;
        }

        const formData = new FormData();

        formData.append(
            "exposure_history",
            document.getElementById("exposure-history").value
        );

        formData.append(
            "infection_information",
            document.getElementById("infection-information").value
        );

        formData.append(
            "risk_level",
            document.getElementById("risk-level").value
        );

        formData.append(
            "clinical_notes",
            document.getElementById("clinical-notes").value
        );

        try {
            const currentRecord = await apiRequest(`/amr/records/${amrRecordId}/`);

            formData.append("status", currentRecord.status);

            const updatedRecord = await apiRequest(
                `/amr/records/${amrRecordId}/update/`,
                {
                    method: "POST",
                    body: formData
                }
            );

            populateRecord(updatedRecord);
            showAlert(
                "assessment-alert",
                "AMR assessment saved successfully.",
                "success"
            );
        } catch (error) {
            showAlert("assessment-alert", error.message);
        }
    }

    async function loadOrganisms() {
        const select = document.getElementById("organism");

        if (!select) {
            return;
        }

        try {
            const data = await apiRequest("/amr/organisms/");

            select.innerHTML = '<option value="">Select organism</option>';

            (data.organisms || []).forEach(organism => {
                const option = document.createElement("option");
                option.value = organism.id;
                option.textContent = `${organism.name} (${organism.code})`;
                select.appendChild(option);
            });
        } catch (error) {
            showAlert("assessment-alert", error.message);
        }
    }

    async function loadAntibiotics() {
        const select = document.getElementById("antibiotic");

        if (!select) {
            return;
        }

        try {
            const data = await apiRequest("/amr/antibiotics/");

            select.innerHTML = '<option value="">Select antibiotic</option>';

            (data.antibiotics || []).forEach(antibiotic => {
                const option = document.createElement("option");
                option.value = antibiotic.id;
                option.textContent = `${antibiotic.name} (${antibiotic.code})`;
                select.appendChild(option);
            });
        } catch (error) {
            showAlert("assessment-alert", error.message);
        }
    }

    async function addResistanceTest(event) {
        event.preventDefault();

        if (!amrRecordId) {
            showAlert("assessment-alert", "No AMR record was selected.");
            return;
        }

        const formData = new FormData();

        formData.append(
            "organism_id",
            document.getElementById("organism").value
        );

        formData.append(
            "antibiotic_id",
            document.getElementById("antibiotic").value
        );

        formData.append(
            "result",
            document.getElementById("result").value
        );

        formData.append(
            "test_notes",
            document.getElementById("test-notes").value
        );

        try {
            await apiRequest(
                `/amr/records/${amrRecordId}/resistance-tests/`,
                {
                    method: "POST",
                    body: formData
                }
            );

            document.getElementById("resistance-test-form").reset();

            const record = await apiRequest(`/amr/records/${amrRecordId}/`);

            renderResistanceTests(record.resistance_tests || []);

            showAlert(
                "assessment-alert",
                "Resistance test added successfully.",
                "success"
            );
        } catch (error) {
            showAlert("assessment-alert", error.message);
        }
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

    async function loadSurveillance() {
        try {
            clearAlert("surveillance-alert");

            const data = await apiRequest("/amr/records/");
            const records = data.records || [];
            const tests = records.flatMap(record => record.resistance_tests || []);
            const resistant = tests.filter(test => test.result === "RESISTANT").length;
            const highRisk = records.filter(
                record => ["HIGH", "URGENT"].includes(record.risk_level)
            ).length;

            document.getElementById("surveillance-records").textContent = records.length;
            document.getElementById("surveillance-tests").textContent = tests.length;
            document.getElementById("resistant-findings").textContent = resistant;
            document.getElementById("surveillance-high-risk").textContent = highRisk;

            renderSurveillance(records);

            const summary = document.getElementById("surveillance-summary");

            if (summary) {
                summary.innerHTML = `
                    <p>
                        ${records.length} AMR record(s), ${tests.length}
                        resistance test(s), and ${resistant}
                        resistant finding(s) are currently available.
                    </p>
                `;
            }
        } catch (error) {
            showAlert("surveillance-alert", error.message);
        }
    }

    function renderSurveillance(records) {
        const table = document.getElementById("surveillance-data");

        if (!table) {
            return;
        }

        const rows = records.flatMap(record =>
            (record.resistance_tests || []).map(test => `
                <tr>
                    <td>${escapeHtml(record.patient_username)}</td>
                    <td>${escapeHtml(test.organism_name)}</td>
                    <td>${escapeHtml(test.antibiotic_name)}</td>
                    <td class="${test.result === "RESISTANT" ? "text-danger fw-bold" : ""}">
                        ${escapeHtml(test.result_display || test.result)}
                    </td>
                    <td class="${riskClass(record.risk_level)}">
                        ${escapeHtml(record.risk_level_display || "Not specified")}
                    </td>
                    <td class="${statusClass(record.status)}">
                        ${escapeHtml(record.status_display || record.status)}
                    </td>
                </tr>
            `)
        );

        table.innerHTML = rows.length
            ? rows.join("")
            : `
                <tr>
                    <td colspan="6" class="text-center">
                        No surveillance data available.
                    </td>
                </tr>
            `;
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

            if (element) {
                element.href = "/amr/surveillance/";
            }
        });
    }

    function setupForms() {
        const assessmentForm = document.getElementById("amr-assessment-form");

        if (assessmentForm) {
            assessmentForm.addEventListener("submit", saveAssessment);
        }

        const resistanceForm = document.getElementById("resistance-test-form");

        if (resistanceForm) {
            resistanceForm.addEventListener("submit", addResistanceTest);
        }
    }

    function setupRefreshButtons() {
        const refreshRecords = document.getElementById("refresh-records");

        if (refreshRecords) {
            refreshRecords.addEventListener("click", loadAllRecords);
        }

        const refreshSurveillance = document.getElementById("refresh-surveillance");

        if (refreshSurveillance) {
            refreshSurveillance.addEventListener("click", loadSurveillance);
        }
    }

    document.addEventListener("DOMContentLoaded", async function () {
        setupNavigation();
        setupForms();
        setupRefreshButtons();

        if (document.getElementById("amr-records")) {
            await loadAllRecords();
        }

        if (document.getElementById("patient-name") || document.getElementById("result-patient")) {
            await loadAmrRecord();
        }

        if (document.getElementById("organism")) {
            await loadOrganisms();
        }

        if (document.getElementById("antibiotic")) {
            await loadAntibiotics();
        }

        if (document.getElementById("surveillance-data")) {
            await loadSurveillance();
        }
    });
})();