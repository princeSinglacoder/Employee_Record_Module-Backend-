// Notification System
let notificationInterval = null;
let userRole = null;

// Keep per-user "seen" state so employee doesn't double-count
function getSeenKey(userName) {
    return `seenLeave_${userName}`;
}

function getSeenSet(userName) {
    try {
        const raw = localStorage.getItem(getSeenKey(userName));
        const arr = raw ? JSON.parse(raw) : [];
        return new Set(Array.isArray(arr) ? arr : []);
    } catch {
        return new Set();
    }
}

function saveSeenSet(userName, set) {
    localStorage.setItem(getSeenKey(userName), JSON.stringify(Array.from(set)));
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
    if (dropdown.classList.contains('show')) {
        window.loadNotifications();
    }
};

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
        if (userRole === 'admin') {
            await loadAdminNotifications(me.userName);
        } else {
            await loadEmployeeNotifications(me.userName);
        }
    } catch (e) {
        // ignore
    }
};

async function loadAdminNotifications(adminUserName) {
    const leavesData = await api.getAllLeaves();
    const leaves = Array.isArray(leavesData) ? leavesData : Object.values(leavesData || {});
    const pending = leaves.filter(l => l.status === 'pending');

    // Seen set is per admin
    const seen = getSeenSet(adminUserName);
    // cleanup: any leave no longer pending should be removed from seen
    for (const l of leaves) {
        if (l.status !== 'pending' && seen.has(l.leave_id)) seen.delete(l.leave_id);
    }
    saveSeenSet(adminUserName, seen);

    const newPending = pending.filter(l => !seen.has(l.leave_id));
    updateNotificationBadge(newPending.length);

    const list = document.getElementById('notificationList');
    if (!list) return;
    if (newPending.length === 0) {
        list.innerHTML = '<div class="no-notifications">No new pending leave requests</div>';
        return;
    }

    list.innerHTML = newPending.map(leave => `
        <div class="notification-item pending">
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
    `).join('');
}

async function loadEmployeeNotifications(employeeUserName) {
    const myLeavesData = await api.getMyLeaves();
    const leaves = Array.isArray(myLeavesData) ? myLeavesData : Object.values(myLeavesData || {});

    // Employee: show only *new* non-pending status updates once
    const seen = getSeenSet(employeeUserName);
    const updates = leaves.filter(l => l.status !== 'pending' && !seen.has(`${l.leave_id}:${l.status}`));

    updateNotificationBadge(updates.length);

    const list = document.getElementById('notificationList');
    if (!list) return;
    if (updates.length === 0) {
        list.innerHTML = '<div class="no-notifications">No new notifications</div>';
        return;
    }

    list.innerHTML = updates.map(leave => {
        const statusClass = leave.status === 'approved' ? 'approved' : 'rejected';
        const icon = leave.status === 'approved' ? '✅' : '❌';
        return `
            <div class="notification-item ${statusClass}" style="cursor: pointer;" onclick="viewLeaveNotificationDetails('${leave.leave_id}')">
                <div class="notification-content">
                    <strong>${icon} Leave ${String(leave.status).toUpperCase()}</strong>
                    <div class="notification-message">
                        Your <strong>${leave.Leave_type || 'leave'}</strong> request (${formatDate(leave.start_date)} to ${formatDate(leave.end_date)}) was <strong>${leave.status}</strong>.
                    </div>
                    <div class="notification-message" style="font-size: 0.85em; color: #666; margin-top: 5px;">Click to view details</div>
                </div>
            </div>
        `;
    }).join('');

    // mark as seen
    for (const leave of updates) {
        seen.add(`${leave.leave_id}:${leave.status}`);
    }
    saveSeenSet(employeeUserName, seen);
}

window.approveLeaveFromNotification = async function (leaveId) {
    const me = await getCurrentUserInfo();
    await api.approveLeave(leaveId);
    // mark seen for admin so it won't count again
    const seen = getSeenSet(me.userName);
    seen.add(leaveId);
    saveSeenSet(me.userName, seen);
    showSuccess('Leave approved successfully');
    if (typeof loadAllLeaves === 'function') loadAllLeaves();
    await window.loadNotifications();
};

window.rejectLeaveFromNotification = async function (leaveId) {
    if (!confirm('Reject this leave request?')) return;
    const me = await getCurrentUserInfo();
    await api.rejectLeave(leaveId);
    const seen = getSeenSet(me.userName);
    seen.add(leaveId);
    saveSeenSet(me.userName, seen);
    showSuccess('Leave rejected');
    if (typeof loadAllLeaves === 'function') loadAllLeaves();
    await window.loadNotifications();
};

window.viewLeaveNotificationDetails = async function (leaveId) {
    try {
        const leave = await api.getLeave(leaveId);
        const statusClass = leave.status === 'approved' ? 'approved' : 'rejected';
        const statusText = leave.status.toUpperCase();
        const icon = leave.status === 'approved' ? '✅' : '❌';
        
        // Create modal content
        const modalContent = `
            <div class="modal-header">
                <h2>${icon} Leave ${statusText}</h2>
                <span class="close" onclick="closeLeaveDetailModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div class="leave-details">
                    <div class="detail-row">
                        <strong>Leave ID:</strong>
                        <span>${leave.leave_id}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Leave Type:</strong>
                        <span>${leave.Leave_type || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Start Date:</strong>
                        <span>${formatDate(leave.start_date)}</span>
                    </div>
                    <div class="detail-row">
                        <strong>End Date:</strong>
                        <span>${formatDate(leave.end_date)}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Reason:</strong>
                        <span>${leave.reason || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Status:</strong>
                        <span><span class="status-badge status-${leave.status}">${statusText}</span></span>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="closeLeaveDetailModal()">Close</button>
            </div>
        `;
        
        const modal = document.getElementById('leaveDetailModal');
        if (modal) {
            modal.querySelector('.modal-content').innerHTML = modalContent;
            modal.style.display = 'block';
        }
        
        // Close notification dropdown
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    } catch (error) {
        showError(`Error loading leave details: ${error.message}`);
    }
};

// Helper function to close leave detail modal
window.closeLeaveDetailModal = function () {
    const modal = document.getElementById('leaveDetailModal');
    if (modal) {
        modal.style.display = 'none';
    }
};

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
    const modal = document.getElementById('leaveDetailModal');
    if (modal && event.target === modal) {
        modal.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    // Start polling only on dashboards (they have the bell button)
    if (!document.getElementById('notificationBadge')) return;
    await window.loadNotifications();
    if (notificationInterval) clearInterval(notificationInterval);
    notificationInterval = setInterval(window.loadNotifications, 5000);
});

