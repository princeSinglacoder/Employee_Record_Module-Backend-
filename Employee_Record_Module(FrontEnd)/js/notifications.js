// Notification System
let notificationInterval = null;
let userRole = null;
let currentUsername = null;

// Helper to get seen set from localStorage
function getSeenSet(userName) {
    try {
        const key = `seenNotifications_${userName}`;
        const raw = localStorage.getItem(key);
        const arr = raw ? JSON.parse(raw) : [];
        return new Set(Array.isArray(arr) ? arr : []);
    } catch {
        return new Set();
    }
}

// Helper to save seen set
function saveSeenSet(userName, set) {
    const key = `seenNotifications_${userName}`;
    localStorage.setItem(key, JSON.stringify(Array.from(set)));
}

// Helper to get system notifications
function getSystemNotifications(userName) {
    try {
        const key = `systemNotifications_${userName}`;
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

// Helper to save system notifications
function saveSystemNotifications(userName, notifications) {
    const key = `systemNotifications_${userName}`;
    localStorage.setItem(key, JSON.stringify(notifications));
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : String(count);
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

window.toggleNotificationDropdown = function () {
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) return;
    dropdown.classList.toggle('show');

    // If opening, mark all currently visible notifications as seen
    if (dropdown.classList.contains('show')) {
        markAllAsSeen();
    }
};

function markAllAsSeen() {
    if (!currentUsername) return;
    const seen = getSeenSet(currentUsername);

    // Select all notification items currently in the list
    const items = document.querySelectorAll('.notification-item');
    items.forEach(item => {
        const id = item.dataset.id;
        if (id) seen.add(id);
    });

    saveSeenSet(currentUsername, seen);
    updateNotificationBadge(0); // Clear badge immediately
}

document.addEventListener('click', (e) => {
    const container = document.querySelector('.notification-container');
    const dropdown = document.getElementById('notificationDropdown');
    if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});

window.loadNotifications = async function () {
    try {
        const me = await getCurrentUserInfo();
        if (!me) return;
        userRole = me.role;
        currentUsername = me.userName;

        if (userRole === 'admin') {
            await loadAdminNotifications(me.userName);
        } else {
            await loadEmployeeNotifications(me.userName);
        }
    } catch (e) {
        console.error("Failed to load notifications:", e);
    }
};

async function loadAdminNotifications(adminUserName) {
    const leavesData = await api.getAllLeaves();
    const leaves = Array.isArray(leavesData) ? leavesData : Object.values(leavesData || {});

    // Admin mainly cares about pending leaves
    const pending = leaves.filter(l => l.status === 'pending');

    // Sort by date (newest first) or leave_id (descending)
    pending.sort((a, b) => b.leave_id - a.leave_id);

    const seen = getSeenSet(adminUserName);

    // Calculate unseen count
    const unseenCount = pending.filter(l => !seen.has(String(l.leave_id))).length;
    updateNotificationBadge(unseenCount);

    const list = document.getElementById('notificationList');
    if (!list) return;

    if (pending.length === 0) {
        list.innerHTML = '<div class="no-notifications">No new pending leave requests</div>';
        return;
    }

    // Render list - show ALL pending requests, not just unseen ones
    list.innerHTML = pending.map(leave => {
        const isSeen = seen.has(String(leave.leave_id));
        return `
        <div class="notification-item pending ${isSeen ? 'seen' : ''}" data-id="${leave.leave_id}">
            <div class="notification-content">
                <strong>${leave.userName || 'Unknown'}</strong> applied for <strong>${leave.Leave_type || 'leave'}</strong>
                <div class="notification-message"><strong>Dates:</strong> ${formatDate(leave.start_date)} to ${formatDate(leave.end_date)}</div>
                <div class="notification-message"><strong>Reason:</strong> ${leave.reason || '-'}</div>
            </div>
            <div class="notification-actions">
                <button class="btn btn-sm btn-success" onclick="approveLeaveFromNotification('${leave.leave_id}')">Approve</button>
                <button class="btn btn-sm btn-danger" onclick="rejectLeaveFromNotification('${leave.leave_id}')">Reject</button>
            </div>
        </div>
    `}).join('');
}

async function loadEmployeeNotifications(employeeUserName) {
    const seen = getSeenSet(employeeUserName);

    // 1. Fetch Leaves (History)
    const myLeavesData = await api.getMyLeaves();
    const leaves = Array.isArray(myLeavesData) ? myLeavesData : Object.values(myLeavesData || {});

    // Filter out pending, show only decisions
    const leaveUpdates = leaves.filter(l => l.status !== 'pending');

    // 2. Check for System Updates (Salary, Dept, etc.)
    const employee = await api.getEmployee(employeeUserName);
    const lastDataKey = `lastEmployeeData_${employeeUserName}`;
    const prevData = JSON.parse(localStorage.getItem(lastDataKey) || '{}');

    let sysNotifs = getSystemNotifications(employeeUserName);
    let newSysNotifs = [];

    // Check Salary
    if (prevData.empSalary && prevData.empSalary !== employee.empSalary) {
        newSysNotifs.push({
            id: `salary_${Date.now()}`,
            type: 'update',
            message: `Your salary has been updated to $${employee.empSalary.toFixed(2)}`,
            timestamp: Date.now()
        });
    }
    // Check Department
    if (prevData.departId && prevData.departId !== employee.departId) {
        newSysNotifs.push({
            id: `dept_${Date.now()}`,
            type: 'update',
            message: `Your department has been updated to ${employee.departId}`,
            timestamp: Date.now()
        });
    }
    // Check Welcome
    if (!prevData.userName && employee.userName) {
        newSysNotifs.push({
            id: `welcome_${Date.now()}`,
            type: 'update',
            message: `Welcome to the company, ${employee.name || employee.userName}!`,
            timestamp: Date.now()
        });
    }

    // Save current state for next diff
    localStorage.setItem(lastDataKey, JSON.stringify(employee));

    // Append new system notifications to persistent storage
    if (newSysNotifs.length > 0) {
        sysNotifs = [...newSysNotifs, ...sysNotifs];
        saveSystemNotifications(employeeUserName, sysNotifs);
    }

    // 3. Combine and Sort
    // We treat leave updates as notifications. ID scheme: "leave_LEAVEID_STATUS"
    // Since we don't have a 'date_updated' field easily, we'll use leave_id as proxy for time for leaves

    const combined = [];

    leaveUpdates.forEach(l => {
        combined.push({
            id: `leave_${l.leave_id}_${l.status}`, // Unique ID for this state
            type: 'leave',
            data: l,
            timestamp: l.leave_id * 1000 // Approximate sortable
        });
    });

    sysNotifs.forEach(n => {
        combined.push({
            id: n.id,
            type: 'system',
            data: n,
            timestamp: n.timestamp
        });
    });

    // Sort by timestamp/ID descending
    combined.sort((a, b) => b.timestamp - a.timestamp);

    // Limit to latest 20 to avoid clutter
    const displayList = combined.slice(0, 20);

    // Calculate badge
    const unseenCount = displayList.filter(item => !seen.has(item.id)).length;
    updateNotificationBadge(unseenCount);

    // Render
    const list = document.getElementById('notificationList');
    if (!list) return;

    if (displayList.length === 0) {
        list.innerHTML = '<div class="no-notifications">No new notifications</div>';
        return;
    }

    list.innerHTML = displayList.map(item => {
        const isSeen = seen.has(item.id);
        if (item.type === 'leave') {
            const l = item.data;
            const statusClass = l.status === 'approved' ? 'approved' : 'rejected';
            const icon = l.status === 'approved' ? '✅' : '❌';
            return `
                <div class="notification-item ${statusClass} ${isSeen ? 'seen' : ''}" data-id="${item.id}" style="cursor: pointer;" onclick="viewLeaveNotificationDetails('${l.leave_id}')">
                    <div class="notification-content">
                        <strong>${icon} Leave ${String(l.status).toUpperCase()}</strong>
                        <div class="notification-message">
                            Your <strong>${l.Leave_type || 'leave'}</strong> request (${formatDate(l.start_date)} to ${formatDate(l.end_date)}) was <strong>${l.status}</strong>.
                        </div>
                    </div>
                </div>
            `;
        } else {
            const msg = item.data.message;
            return `
                <div class="notification-item update ${isSeen ? 'seen' : ''}" data-id="${item.id}">
                    <div class="notification-content">
                        ${msg}
                    </div>
                </div>
            `;
        }
    }).join('');
}

// Leave actions
window.approveLeaveFromNotification = async function (leaveId) {
    try {
        await api.approveLeave(leaveId);
        showSuccess('Leave approved successfully');
        if (typeof loadAllLeaves === 'function') loadAllLeaves(); // Refresh main table if on admin page
        await window.loadNotifications(); // Refresh notifications
    } catch (e) {
        showError(e.message);
    }
};

window.rejectLeaveFromNotification = async function (leaveId) {
    if (!confirm('Reject this leave request?')) return;
    try {
        await api.rejectLeave(leaveId);
        showSuccess('Leave rejected');
        if (typeof loadAllLeaves === 'function') loadAllLeaves();
        await window.loadNotifications();
    } catch (e) {
        showError(e.message);
    }
};

// View leave details modal
window.viewLeaveNotificationDetails = async function (leaveId) {
    try {
        const leave = await api.getLeave(leaveId);
        const modal = document.getElementById('leaveDetailModal');
        const content = modal.querySelector('.modal-content');

        content.innerHTML = `
            <span class="close" onclick="document.getElementById('leaveDetailModal').style.display='none'">&times;</span>
            <h2>Leave Details</h2>
            <div class="detail-row"><strong>Type:</strong> ${leave.Leave_type}</div>
            <div class="detail-row"><strong>Dates:</strong> ${formatDate(leave.start_date)} to ${formatDate(leave.end_date)}</div>
            <div class="detail-row"><strong>Reason:</strong> ${leave.reason}</div>
            <div class="detail-row"><strong>Status:</strong> <span class="status-badge ${leave.status}">${leave.status.toUpperCase()}</span></div>
        `;

        modal.style.display = 'block';
    } catch (e) {
        console.error(e);
    }
};

// Close modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('leaveDetailModal');
    if (modal && event.target === modal) modal.style.display = 'none';
});

// Start polling
document.addEventListener('DOMContentLoaded', async () => {
    if (!document.getElementById('notificationBadge')) return;
    await window.loadNotifications();
    if (notificationInterval) clearInterval(notificationInterval);
    notificationInterval = setInterval(window.loadNotifications, 5000);
});
