// Employee Dashboard Logic
let currentUserInfo = null;

document.addEventListener('DOMContentLoaded', async () => {
    currentUserInfo = await checkAuth();
    if (!currentUserInfo || currentUserInfo.role !== 'employee') {
        return;
    }

    // Load initial data
    loadProfile();
    loadMyLeaves();

    // Setup form handlers
    setupFormHandlers();
});

// Section navigation
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all sidebar buttons
    document.querySelectorAll('.sidebar-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Load profile
async function loadProfile() {
    try {
        const userInfo = await getCurrentUserInfo();
        if (!userInfo) {
            showError('Unable to load user information');
            return;
        }

        const employee = await api.getEmployee(userInfo.userName);
        
        document.getElementById('profileUsername').textContent = employee.userName || '-';
        document.getElementById('profileName').textContent = employee.empName || '-';
        document.getElementById('profileAge').textContent = employee.empAge || '-';
        document.getElementById('profileSalary').textContent = employee.empSalary ? `$${employee.empSalary.toFixed(2)}` : '-';
        document.getElementById('profileDepartId').textContent = employee.departId || '-';
        
        // Update the navbar display with employee name
        const currentUserSpan = document.getElementById('currentUser');
        if (currentUserSpan && employee.empName) {
            currentUserSpan.textContent = employee.empName;
        }
    } catch (error) {
        showError(`Error loading profile: ${error.message}`);
    }
}

// Load my leaves
async function loadMyLeaves() {
    try {
        const myLeavesData = await api.getMyLeaves();
        const tbody = document.getElementById('myLeavesTableBody');
        
        // Convert dictionary to array if needed
        const myLeaves = Array.isArray(myLeavesData) 
            ? myLeavesData 
            : Object.values(myLeavesData || {});
        
        if (!myLeaves || myLeaves.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">No leave requests found</td></tr>';
            return;
        }

        tbody.innerHTML = myLeaves.map(leave => `
            <tr>
                <td>${leave.leave_id || '-'}</td>
                <td>${leave.Leave_type || '-'}</td>
                <td>${formatDate(leave.start_date)}</td>
                <td>${formatDate(leave.end_date)}</td>
                <td>${leave.reason || '-'}</td>
                <td><span class="status-badge status-${leave.status}">${leave.status || 'pending'}</span></td>
                <td>
                    ${leave.status === 'pending' ? `
                        <button class="btn btn-sm btn-primary" onclick="openEditLeaveModal('${leave.leave_id}')">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteMyLeave('${leave.leave_id}')">Delete</button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('myLeavesTableBody').innerHTML = 
            `<tr><td colspan="7" class="error">Error: ${error.message}</td></tr>`;
    }
}

// Setup form handlers
function setupFormHandlers() {
    // Apply leave form
    const applyLeaveForm = document.getElementById('applyLeaveForm');
    if (applyLeaveForm) {
        applyLeaveForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultDiv = document.getElementById('applyLeaveResult');
            
            const leaveData = {
                Leave_type: document.getElementById('leaveType').value,
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value,
                reason: document.getElementById('leaveReason').value
            };

            try {
                await api.applyLeave(leaveData);
                resultDiv.innerHTML = '<div class="success-message">Leave applied successfully</div>';
                applyLeaveForm.reset();
                loadMyLeaves();
                // Reload notifications (admin will see new pending leave)
                if (typeof window.loadNotifications === 'function') {
                    await window.loadNotifications();
                }
                showSuccess('Leave applied successfully');
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
                showError(error.message);
            }
        });
    }

    // Edit leave form
    const editLeaveForm = document.getElementById('editLeaveForm');
    if (editLeaveForm) {
        editLeaveForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const leaveId = document.getElementById('editLeaveId').value;
            const updateData = {};
            
            const leaveType = document.getElementById('editLeaveType').value;
            const startDate = document.getElementById('editStartDate').value;
            const endDate = document.getElementById('editEndDate').value;
            const reason = document.getElementById('editLeaveReason').value;

            if (leaveType) updateData.Leave_type = leaveType;
            if (startDate) updateData.start_date = startDate;
            if (endDate) updateData.end_date = endDate;
            if (reason) updateData.reason = reason;

            try {
                await api.updateLeave(leaveId, updateData);
                closeEditLeaveModal();
                loadMyLeaves();
                showSuccess('Leave updated successfully');
            } catch (error) {
                showError(error.message);
            }
        });
    }
}

// Open edit leave modal
async function openEditLeaveModal(leaveId) {
    try {
        const leave = await api.getLeave(leaveId);
        document.getElementById('editLeaveId').value = leave.leave_id;
        document.getElementById('editLeaveType').value = leave.Leave_type || '';
        document.getElementById('editStartDate').value = leave.start_date || '';
        document.getElementById('editEndDate').value = leave.end_date || '';
        document.getElementById('editLeaveReason').value = leave.reason || '';
        document.getElementById('editLeaveModal').style.display = 'block';
    } catch (error) {
        showError(error.message);
    }
}

// Close edit leave modal
function closeEditLeaveModal() {
    document.getElementById('editLeaveModal').style.display = 'none';
}

// Delete my leave
async function deleteMyLeave(leaveId) {
    if (!confirm('Are you sure you want to delete this leave request?')) {
        return;
    }

    try {
        await api.deleteLeave(leaveId);
        loadMyLeaves();
        showSuccess('Leave deleted successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const editLeaveModal = document.getElementById('editLeaveModal');
    if (event.target === editLeaveModal) {
        editLeaveModal.style.display = 'none';
    }
}
