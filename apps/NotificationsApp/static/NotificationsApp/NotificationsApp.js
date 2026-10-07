document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("notifications-container");
    const messageContainer = document.getElementById("notification-message");
    const totalCount = document.getElementById("total-count");
    const unreadCount = document.getElementById("unread-count");
    const readCount = document.getElementById("read-count");
    const refreshButton = document.getElementById("refresh-btn");
    const markAllReadButton = document.getElementById("mark-all-read-btn");
    const deleteReadButton = document.getElementById("delete-read-btn");

    if (!container) {
        return;
    }

    const currentPath = window.location.pathname;
    const unreadOnly = currentPath.includes("/notifications/unread/");

    const endpoints = {
        all: "/notifications/api/records/",
        unread: "/notifications/api/records/unread/",
        read: "/notifications/api/records/read/",
        markAllRead: "/notifications/api/records/mark-all-read/",
        deleteRead: "/notifications/api/records/delete-read/",
    };

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

    function escapeHtml(value) {
        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function showMessage(message, type = "success") {
        messageContainer.innerHTML = `
            <div class="alert alert-${type} alert-message" role="alert">
                ${escapeHtml(message)}
            </div>
        `;

        window.setTimeout(() => {
            messageContainer.innerHTML = "";
        }, 4000);
    }

    function formatDate(value) {
        if (!value) {
            return "Unknown date";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString();
    }

    function priorityClass(priority) {
        return `priority-${String(priority || "normal").toLowerCase()}`;
    }

    function renderNotification(notification) {
        const readClass = notification.is_read ? "" : "unread";

        const readBadge = notification.is_read
            ? '<span class="notification-badge badge-read">Read</span>'
            : '<span class="notification-badge badge-unread">Unread</span>';

        const actionButton = notification.is_read
            ? `
                <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary mark-unread-btn"
                    data-id="${notification.id}"
                >
                    Mark Unread
                </button>
            `
            : `
                <button
                    type="button"
                    class="btn btn-sm btn-outline-primary mark-read-btn"
                    data-id="${notification.id}"
                >
                    Mark Read
                </button>
            `;

        return `
            <div class="notification-item ${readClass}" data-id="${notification.id}">
                <div class="notification-content">
                    <div class="d-flex justify-content-between align-items-start gap-3">
                        <div>
                            <h3 class="notification-title">
                                ${escapeHtml(notification.title)}
                            </h3>

                            <div class="notification-meta">
                                <span>
                                    ${escapeHtml(notification.notification_type_display)}
                                </span>

                                <span class="notification-badge ${priorityClass(notification.priority)}">
                                    ${escapeHtml(notification.priority_display)}
                                </span>

                                ${readBadge}
                            </div>
                        </div>
                    </div>

                    <p class="notification-message mt-3">
                        ${escapeHtml(notification.message)}
                    </p>

                    <div class="notification-meta">
                        <span>
                            ${escapeHtml(formatDate(notification.created_at))}
                        </span>

                        ${
                            notification.patient_name
                                ? `<span>Patient: ${escapeHtml(notification.patient_name)}</span>`
                                : ""
                        }
                    </div>

                    <div class="notification-actions">
                        ${actionButton}

                        ${
                            notification.action_url
                                ? `
                                    <a
                                        href="${escapeHtml(notification.action_url)}"
                                        class="btn btn-sm btn-outline-primary"
                                    >
                                        Open
                                    </a>
                                `
                                : ""
                        }

                        <button
                            type="button"
                            class="btn btn-sm btn-outline-danger delete-btn"
                            data-id="${notification.id}"
                        >
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function renderNotifications(notifications) {
        if (!notifications || notifications.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No notifications</h3>
                    <p>
                        ${
                            unreadOnly
                                ? "You currently have no unread notifications."
                                : "There are no notifications to display."
                        }
                    </p>
                </div>
            `;

            return;
        }

        container.innerHTML = notifications
            .map(renderNotification)
            .join("");
    }

    function updateStats(notifications) {
        if (!totalCount || !unreadCount || !readCount) {
            return;
        }

        const total = notifications.length;
        const unread = notifications.filter(
            notification => !notification.is_read
        ).length;

        totalCount.textContent = total;
        unreadCount.textContent = unread;
        readCount.textContent = total - unread;
    }

    async function fetchNotifications() {
        container.innerHTML = `
            <div class="text-center py-5">
                Loading notifications...
            </div>
        `;

        const endpoint = unreadOnly
            ? endpoints.unread
            : endpoints.all;

        try {
            const response = await fetch(endpoint, {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(
                    `Request failed with status ${response.status}.`
                );
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(
                    data.message || "Unable to load notifications."
                );
            }

            renderNotifications(data.notifications);
            updateStats(data.notifications);
        } catch (error) {
            console.error("Notification loading error:", error);

            container.innerHTML = `
                <div class="empty-state">
                    <h3>Unable to load notifications</h3>
                    <p>Please refresh the page and try again.</p>
                </div>
            `;

            showMessage(
                "Failed to load notifications.",
                "danger"
            );
        }
    }

    async function postRequest(url) {
        const csrfToken = getCookie("csrftoken");

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json",
            },
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Request failed."
            );
        }

        return data;
    }

    async function markNotificationRead(notificationId) {
        try {
            await postRequest(
                `/notifications/api/records/${notificationId}/read/`
            );

            showMessage(
                "Notification marked as read."
            );

            await fetchNotifications();
        } catch (error) {
            console.error(error);
            showMessage(
                error.message || "Unable to mark notification as read.",
                "danger"
            );
        }
    }

    async function markNotificationUnread(notificationId) {
        try {
            await postRequest(
                `/notifications/api/records/${notificationId}/unread/`
            );

            showMessage(
                "Notification marked as unread."
            );

            await fetchNotifications();
        } catch (error) {
            console.error(error);
            showMessage(
                error.message || "Unable to mark notification as unread.",
                "danger"
            );
        }
    }

    async function deleteNotification(notificationId) {
        const confirmed = window.confirm(
            "Delete this notification?"
        );

        if (!confirmed) {
            return;
        }

        try {
            await postRequest(
                `/notifications/api/records/${notificationId}/delete/`
            );

            showMessage(
                "Notification deleted successfully."
            );

            await fetchNotifications();
        } catch (error) {
            console.error(error);
            showMessage(
                error.message || "Unable to delete notification.",
                "danger"
            );
        }
    }

    async function markAllAsRead() {
        try {
            const data = await postRequest(
                endpoints.markAllRead
            );

            showMessage(
                data.message || "All notifications marked as read."
            );

            await fetchNotifications();
        } catch (error) {
            console.error(error);
            showMessage(
                error.message || "Unable to mark notifications as read.",
                "danger"
            );
        }
    }

    async function deleteReadNotifications() {
        const confirmed = window.confirm(
            "Delete all read notifications?"
        );

        if (!confirmed) {
            return;
        }

        try {
            const data = await postRequest(
                endpoints.deleteRead
            );

            showMessage(
                data.message || "Read notifications deleted successfully."
            );

            await fetchNotifications();
        } catch (error) {
            console.error(error);
            showMessage(
                error.message || "Unable to delete read notifications.",
                "danger"
            );
        }
    }

    container.addEventListener("click", event => {
        const markReadButton = event.target.closest(
            ".mark-read-btn"
        );

        if (markReadButton) {
            markNotificationRead(
                markReadButton.dataset.id
            );

            return;
        }

        const markUnreadButton = event.target.closest(
            ".mark-unread-btn"
        );

        if (markUnreadButton) {
            markNotificationUnread(
                markUnreadButton.dataset.id
            );

            return;
        }

        const deleteButton = event.target.closest(
            ".delete-btn"
        );

        if (deleteButton) {
            deleteNotification(
                deleteButton.dataset.id
            );
        }
    });

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            fetchNotifications
        );
    }

    if (markAllReadButton) {
        markAllReadButton.addEventListener(
            "click",
            markAllAsRead
        );
    }

    if (deleteReadButton) {
        deleteReadButton.addEventListener(
            "click",
            deleteReadNotifications
        );
    }

    fetchNotifications();
});