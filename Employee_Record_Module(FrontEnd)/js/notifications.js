// Notification System
let notificationInterval = null;
let lastCheckedLeaves = {};
let seenLeaveIds = new Set(); // Track which leaves admin has seen/acknowledged
window.seenLeaveIds = seenLeaveIds; // Make it globally accessible
let userRole = null;
let currentUserName = null;

// Initialize notifications
document.addEventListener('DOMContentLoaded', async () => {
    // Get user info
    const userInfo = await getCurrentUserInfo();
    if (userInfo) {
        userRole = userInfo.role;
        currentUserName = userInfo.userName;
        
        // Start polling for notifications
        startNotificationPolling();
        
        // Load initial notifications
        await loadNotifications();
    }
});

// Start polling for notifications every 5 seconds
function startNotificationPolling() {
    // Clear any existing interval
    if (notificationInterval) {
        clearInterval(notificationInterval);
    }
    
    // Poll every 5 seconds
    notificationInterval = setInterval(async () => {
        await loadNotifications();
    }, 5000);
}

// Stop polling
function stopNotificationPolling() {
    if (notificationInterval) {
        clearInterval(notificationInterval);
        notificationInterval = null;
    }
}

// Toggle notification dropdown (make it globally accessible)
window.toggleNotificationDropdown = function() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
        if (dropdown.classList.contains('show')) {
            window.loadNotifications();
        }
    }
};

// Close notification dropdown when clicking outside
document.addEventListener('click', (e) => {
    const container = document.querySelector('.notification-container');
    const dropdown = document.getElementById('notificationDropdown');
    
    if (container && dropdown && !container.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});

// Load notifications based on user role (make it globally accessible)
window.loadNotifications = async function() {
    if (!userRole) return;
    
    try {
        if (userRole === 'admin') {
            await loadAdminNotifications();
        } else {
            await loadEmployeeNotifications();
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
};

// Load admin notifications (pending leaves)
async function loadAdminNotifications() {
    try {
        const allLeaves = await api.getAllLeaves();
        const leavesArray = Array.isArray(allLeaves) 
            ? allLeaves 
            : Object.values(allLeaves || {});
        
        // Filter pending leaves
        const pendingLeaves = leavesArray.filter(leave => leave.status === 'pending');
        
        // Filter out leaves that are no longer pending (were approved/rejected)
        // Remove them from seen list
        leavesArray.forEach(leave => {
            if (leave.status !== 'pending' && seenLeaveIds.has(leave.leave_id)) {
                seenLeaveIds.delete(leave.leave_id);
            }
        });
        
        // Only show new pending leaves that haven't been seen
        const newPendingLeaves = pendingLeaves.filter(leave => !seenLeaveIds.has(leave.leave_id));
        
        // Update badge with count of new pending leaves
        updateNotificationBadge(newPendingLeaves.length);
        
        // Update notification list
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;
        
        if (newPendingLeaves.length === 0) {
            notificationList.innerHTML = '<div class="no-notifications">No new pending leave requests</div>';
            return;
        }
        
        notificationList.innerHTML = newPendingLeaves.map(leave => `
            <div class="notification-item pending">
                <div class="notification-content">
                    <strong>${leave.userName || 'Unknown'}</strong> applied for <strong>${leave.Leave_type || 'leave'}</strong>
                    <div class="notification-message">
                        <strong>Dates:</strong> ${formatDate(leave.start_date)} to ${formatDate(leave.end_date)}
                    </div>
                    <div class="notification-message">
                        <strong>Reason:</strong> ${leave.reason || 'No reason provided'}
                    </div>
                </div>
                <div class="notification-actions">
                    <button class="btn btn-sm btn-success" onclick="approveLeaveFromNotification('${leave.leave_id}')">Approve</button>
                    <button class="btn btn-sm btn-danger" onclick="rejectLeaveFromNotification('${leave.leave_id}')">Reject</button>
                </div>
            </div>
        `).join('');
        
        // Store for comparison
        lastCheckedLeaves = {};
        pendingLeaves.forEach(leave => {
            lastCheckedLeaves[leave.leave_id] = leave.status;
        });
    } catch (error) {
        console.error('Error loading admin notifications:', error);
    }
}

// Load employee notifications (status changes)
async function loadEmployeeNotifications() {
    try {
        const myLeaves = await api.getMyLeaves();
        const leavesArray = Array.isArray(myLeaves) 
            ? myLeaves 
            : Object.values(myLeaves || {});
        
        // Filter leaves that are approved or rejected (not pending)
        const statusChangedLeaves = leavesArray.filter(leave => {
            const previousStatus = lastCheckedLeaves[leave.leave_id];
            return leave.status !== 'pending' && previousStatus !== leave.status;
        });
        
        // Update badge with new notifications
        const newNotifications = statusChangedLeaves.filter(leave => {
            return !lastCheckedLeaves[leave.leave_id] || lastCheckedLeaves[leave.leave_id] === 'pending';
        });
        
        updateNotificationBadge(newNotifications.length);
        
        // Update notification list
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;
        
        if (statusChangedLeaves.length === 0 && leavesArray.length === 0) {
            notificationList.innerHTML = '<div class="no-notifications">No notifications</div>';
            return;
        }
        
        // Show all non-pending leaves as notifications
        const nonPendingLeaves = leavesArray.filter(leave => leave.status !== 'pending');
        
        if (nonPendingLeaves.length === 0) {
            notificationList.innerHTML = '<div class="no-notifications">No notifications</div>';
            return;
        }
        
        notificationList.innerHTML = nonPendingLeaves.map(leave => {
            const statusClass = leave.status === 'approved' ? 'approved' : 'rejected';
            const statusIcon = leave.status === 'approved' ? '✅' : '❌';
            return `
                <div class="notification-item ${statusClass}">
                    <div class="notification-content">
                        <strong>${statusIcon} Leave ${leave.status.toUpperCase()}</strong>
                        <div class="notification-message">
                            Your <strong>${leave.Leave_type || 'leave'}</strong> request from ${formatDate(leave.start_date)} to ${formatDate(leave.end_date)} has been <strong>${leave.status}</strong>.
                        </div>
                        ${leave.reason ? `<div class="notification-message"><strong>Reason:</strong> ${leave.reason}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        // Store current statuses
        lastCheckedLeaves = {};
        leavesArray.forEach(leave => {
            lastCheckedLeaves[leave.leave_id] = leave.status;
        });
    } catch (error) {
        console.error('Error loading employee notifications:', error);
    }
}

// Update notification badge
function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Approve leave from notification (admin) - make globally accessible
window.approveLeaveFromNotification = async function(leaveId) {
    try {
        await api.approveLeave(leaveId);
        // Mark this leave as seen (approved)
        seenLeaveIds.add(leaveId);
        showSuccess('Leave approved successfully');
        await window.loadNotifications();
        // Reload leaves table if on leaves page
        if (typeof loadAllLeaves === 'function') {
            loadAllLeaves();
        }
    } catch (error) {
        showError(error.message);
    }
};

// Reject leave from notification (admin) - make globally accessible
window.rejectLeaveFromNotification = async function(leaveId) {
    if (!confirm('Are you sure you want to reject this leave request?')) {
        return;
    }
    
    try {
        await api.rejectLeave(leaveId);
        // Mark this leave as seen (rejected)
        seenLeaveIds.add(leaveId);
        showSuccess('Leave rejected');
        await window.loadNotifications();
        // Reload leaves table if on leaves page
        if (typeof loadAllLeaves === 'function') {
            loadAllLeaves();
        }
    } catch (error) {
        showError(error.message);
    }
};

// Clear notification badge (when user views notifications)
function clearNotificationBadge() {
    updateNotificationBadge(0);
    // Reset last checked leaves to current state
    lastCheckedLeaves = {};
}
