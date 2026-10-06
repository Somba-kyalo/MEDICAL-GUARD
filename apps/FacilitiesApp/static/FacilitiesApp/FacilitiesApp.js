document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    if (path.includes("/facilities/list/")) {
        initializeFacilityList();
    }

    if (path.includes("/facilities/detail/")) {
        initializeFacilityDetail();
    }

    if (path.includes("/facilities/map/")) {
        initializeFacilityMap();
    }

    if (path.includes("/facilities/resources")) {
        initializeFacilityResources();
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
    const container = document.querySelector("#facility-message");

    if (!container) {
        alert(message);
        return;
    }

    container.className = `alert alert-${type}`;
    container.textContent = message;
    container.classList.remove("d-none");
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

async function initializeFacilityList() {
    const container = document.querySelector("#facilities-container");

    if (!container) {
        return;
    }

    try {
        const data = await request("/facilities/api/records/");
        renderFacilityList(container, data.facilities || []);
        updateFacilitySummary(data.facilities || []);
        initializeFacilityFilters(container);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

function renderFacilityList(container, facilities) {
    if (!facilities.length) {
        container.innerHTML = `
            <div class="empty-state">
                <h5>No facilities found</h5>
                <p class="text-muted mb-0">
                    There are currently no facilities available.
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = facilities.map(facility => `
        <div class="facility-item">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                    <h5 class="facility-name mb-1">
                        ${escapeHtml(facility.name)}
                    </h5>

                    <div class="facility-meta mb-2">
                        ${escapeHtml(facility.facility_type_display)}
                        · ${escapeHtml(facility.facility_code)}
                    </div>

                    <p class="mb-1">
                        <strong>Location:</strong>
                        ${escapeHtml(facility.county)}
                        ${facility.sub_county
                            ? `, ${escapeHtml(facility.sub_county)}`
                            : ""}
                    </p>

                    <p class="mb-1">
                        <strong>Referral:</strong>
                        ${facility.referral_available ? "Available" : "Not Available"}
                    </p>

                    <p class="mb-0 facility-services">
                        <strong>Services:</strong>
                        ${escapeHtml(facility.services || "Not specified")}
                    </p>
                </div>

                <div class="text-md-end">
                    <span class="badge ${getStatusClass(facility.operating_status)}">
                        ${escapeHtml(facility.operating_status_display)}
                    </span>

                    <div class="mt-3">
                        <a
                            href="/facilities/detail/${facility.id}/"
                            class="btn btn-sm btn-outline-primary"
                        >
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

function updateFacilitySummary(facilities) {
    const total = document.querySelector("#total-facilities");
    const active = document.querySelector("#active-facilities");
    const referral = document.querySelector("#referral-facilities");

    if (total) {
        total.textContent = facilities.length;
    }

    if (active) {
        active.textContent = facilities.filter(
            facility => facility.operating_status === "ACTIVE"
        ).length;
    }

    if (referral) {
        referral.textContent = facilities.filter(
            facility => facility.referral_available
        ).length;
    }
}

function initializeFacilityFilters(container) {
    const allButton = document.querySelector("#show-all-facilities");
    const activeButton = document.querySelector("#show-active-facilities");
    const referralButton = document.querySelector("#show-referral-facilities");

    if (allButton) {
        allButton.addEventListener("click", async () => {
            await loadFacilities(
                container,
                "/facilities/api/records/",
                allButton,
                [activeButton, referralButton]
            );
        });
    }

    if (activeButton) {
        activeButton.addEventListener("click", async () => {
            await loadFacilities(
                container,
                "/facilities/api/records/active/",
                activeButton,
                [allButton, referralButton]
            );
        });
    }

    if (referralButton) {
        referralButton.addEventListener("click", async () => {
            await loadFacilities(
                container,
                "/facilities/api/records/referral/",
                referralButton,
                [allButton, activeButton]
            );
        });
    }
}

async function loadFacilities(container, url, activeButton, otherButtons) {
    try {
        const data = await request(url);
        renderFacilityList(container, data.facilities || []);

        if (activeButton) {
            activeButton.classList.remove("btn-outline-primary");
            activeButton.classList.add("btn-primary");
        }

        otherButtons.forEach(button => {
            if (!button) {
                return;
            }

            button.classList.remove("btn-primary");
            button.classList.add("btn-outline-primary");
        });
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

async function initializeFacilityDetail() {
    const container = document.querySelector("#facility-detail");

    if (!container) {
        return;
    }

    const facilityId = container.dataset.facilityId;

    if (!facilityId) {
        container.innerHTML = `
            <div class="alert alert-danger">
                Facility ID is missing.
            </div>
        `;
        return;
    }

    try {
        const facility = await request(
            `/facilities/api/records/${facilityId}/`
        );

        renderFacilityDetail(container, facility);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

function renderFacilityDetail(container, facility) {
    const resources = facility.resources || [];

    container.innerHTML = `
        <div class="card facility-card">
            <div class="card-body">
                <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                    <div>
                        <h2 class="facility-name mb-1">
                            ${escapeHtml(facility.name)}
                        </h2>

                        <p class="facility-meta mb-0">
                            ${escapeHtml(facility.facility_code)}
                            · ${escapeHtml(facility.facility_type_display)}
                        </p>
                    </div>

                    <div>
                        <span class="badge ${getStatusClass(facility.operating_status)}">
                            ${escapeHtml(facility.operating_status_display)}
                        </span>
                    </div>
                </div>

                <div class="facility-detail-section">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="detail-label">County</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.county)}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Sub County</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.sub_county || "Not specified")}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Address</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.address || "Not specified")}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Phone</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.phone_number || "Not specified")}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Email</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.email || "Not specified")}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Referral Availability</div>
                            <div class="detail-value">
                                ${facility.referral_available
                                    ? "Available"
                                    : "Not Available"}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="facility-detail-section">
                    <h5>Services</h5>
                    <p class="facility-services mb-0">
                        ${escapeHtml(facility.services || "No services specified.")}
                    </p>
                </div>

                <div class="facility-detail-section">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">Resources</h5>

                        <a
                            href="/facilities/resources/${facility.id}/"
                            class="btn btn-sm btn-outline-primary"
                        >
                            View Resources
                        </a>
                    </div>

                    ${renderResourcePreview(resources)}
                </div>

                <div class="facility-detail-section">
                    <h5>Location Coordinates</h5>

                    <div class="row">
                        <div class="col-md-6">
                            <div class="detail-label">Latitude</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.latitude || "Not available")}
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-label">Longitude</div>
                            <div class="detail-value">
                                ${escapeHtml(facility.longitude || "Not available")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderResourcePreview(resources) {
    if (!resources.length) {
        return `
            <div class="empty-state">
                <p class="text-muted mb-0">
                    No resources have been recorded for this facility.
                </p>
            </div>
        `;
    }

    return resources.slice(0, 5).map(resource => `
        <div class="resource-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="resource-name">
                        ${escapeHtml(resource.name)}
                    </div>

                    <small class="text-muted">
                        ${escapeHtml(resource.category_display)}
                    </small>
                </div>

                <div class="text-end">
                    <div class="resource-quantity">
                        ${resource.quantity}
                    </div>

                    <small class="resource-available">
                        ${resource.available ? "Available" : "Unavailable"}
                    </small>
                </div>
            </div>
        </div>
    `).join("");
}

async function initializeFacilityMap() {
    const mapContainer = document.querySelector(
        "#facility-map-container"
    );

    const listContainer = document.querySelector(
        "#map-facilities-container"
    );

    if (!mapContainer || !listContainer) {
        return;
    }

    try {
        const data = await request(
            "/facilities/api/records/active/"
        );

        const facilities = data.facilities || [];

        renderFacilityMap(mapContainer, facilities);
        renderMapFacilityList(listContainer, facilities);
    } catch (error) {
        mapContainer.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

function renderFacilityMap(container, facilities) {
    const locatedFacilities = facilities.filter(
        facility =>
            facility.latitude !== null &&
            facility.longitude !== null
    );

    if (!locatedFacilities.length) {
        container.innerHTML = `
            <div class="map-placeholder">
                <div>
                    <h5>No facility coordinates available</h5>
                    <p class="text-muted mb-0">
                        Facilities with recorded coordinates will appear here.
                    </p>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="map-placeholder">
            <div>
                <h5>Facility Locations</h5>
                <p class="text-muted">
                    ${locatedFacilities.length} active facilities have location coordinates.
                </p>

                <div class="row g-2 text-start">
                    ${locatedFacilities.map(facility => `
                        <div class="col-md-6">
                            <div class="map-location">
                                <strong>
                                    ${escapeHtml(facility.name)}
                                </strong>

                                <div class="small text-muted">
                                    ${escapeHtml(facility.latitude)},
                                    ${escapeHtml(facility.longitude)}
                                </div>

                                <a
                                    href="/facilities/detail/${facility.id}/"
                                    class="btn btn-sm btn-outline-primary mt-2"
                                >
                                    Details
                                </a>
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
        </div>
    `;
}

function renderMapFacilityList(container, facilities) {
    const locatedFacilities = facilities.filter(
        facility =>
            facility.latitude !== null &&
            facility.longitude !== null
    );

    if (!locatedFacilities.length) {
        container.innerHTML = `
            <p class="text-muted mb-0">
                No facilities with coordinates found.
            </p>
        `;
        return;
    }

    container.innerHTML = locatedFacilities.map(facility => `
        <div class="map-location">
            <div class="d-flex justify-content-between gap-3">
                <div>
                    <strong>
                        ${escapeHtml(facility.name)}
                    </strong>

                    <div class="small text-muted">
                        ${escapeHtml(facility.county)}
                    </div>
                </div>

                <a
                    href="/facilities/detail/${facility.id}/"
                    class="btn btn-sm btn-outline-primary"
                >
                    View
                </a>
            </div>
        </div>
    `).join("");
}

async function initializeFacilityResources() {
    const container = document.querySelector(
        "#facility-resources"
    );

    if (!container) {
        return;
    }

    const facilityId = container.dataset.facilityId;

    try {
        if (facilityId) {
            const data = await request(
                `/facilities/api/records/${facilityId}/resources/`
            );

            renderFacilityResources(
                container,
                data.facility,
                data.resources || []
            );

            return;
        }

        const data = await request(
            "/facilities/api/records/active/"
        );

        renderAllFacilityResources(
            container,
            data.facilities || []
        );
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

function renderFacilityResources(container, facility, resources) {
    container.innerHTML = `
        <div class="card facility-card">
            <div class="card-body">
                <div class="mb-4">
                    <h3 class="facility-name mb-1">
                        ${escapeHtml(facility.name)}
                    </h3>

                    <p class="text-muted mb-0">
                        ${escapeHtml(facility.facility_code)}
                    </p>
                </div>

                ${renderResourceList(resources)}
            </div>
        </div>
    `;
}

function renderAllFacilityResources(container, facilities) {
    if (!facilities.length) {
        container.innerHTML = `
            <div class="empty-state">
                <h5>No facilities found</h5>
                <p class="text-muted mb-0">
                    There are currently no active facilities.
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = facilities.map(facility => `
        <div class="card facility-card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h5 class="facility-name mb-1">
                            ${escapeHtml(facility.name)}
                        </h5>

                        <small class="text-muted">
                            ${escapeHtml(facility.facility_code)}
                        </small>
                    </div>

                    <a
                        href="/facilities/resources/${facility.id}/"
                        class="btn btn-sm btn-outline-primary"
                    >
                        View
                    </a>
                </div>

                ${renderResourceList(facility.resources || [])}
            </div>
        </div>
    `).join("");
}

function renderResourceList(resources) {
    if (!resources.length) {
        return `
            <div class="empty-state">
                <p class="text-muted mb-0">
                    No resources recorded.
                </p>
            </div>
        `;
    }

    return resources.map(resource => `
        <div class="resource-item">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <div class="resource-name">
                        ${escapeHtml(resource.name)}
                    </div>

                    <small class="text-muted">
                        ${escapeHtml(resource.category_display)}
                    </small>
                </div>

                <div class="col-md-3">
                    <span class="resource-quantity">
                        ${resource.quantity}
                    </span>
                </div>

                <div class="col-md-3 text-md-end">
                    <span class="badge ${
                        resource.available
                            ? "bg-success"
                            : "bg-secondary"
                    }">
                        ${resource.available ? "Available" : "Unavailable"}
                    </span>
                </div>
            </div>
        </div>
    `).join("");
}

function getStatusClass(status) {
    const classes = {
        ACTIVE: "bg-success",
        INACTIVE: "bg-secondary",
        TEMPORARILY_CLOSED: "bg-warning text-dark"
    };

    return classes[status] || "bg-secondary";
}