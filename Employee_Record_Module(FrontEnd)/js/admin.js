// Admin Dashboard Logic
let currentUserInfo = null;

document.addEventListener('DOMContentLoaded', async () => {
    currentUserInfo = await checkAuth();
    if (!currentUserInfo || currentUserInfo.role !== 'admin') {
        return;
    }

    // ------------------ WebSocket for notifications ------------------
    const employee_id = currentUserInfo.id; // or currentUserInfo.employee_id
    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/notifications/${employee_id}`);

    socket.onopen = () => {
        console.log("WebSocket connected for notifications");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        alert(`Notification: ${data.message}`); // later you can replace with toast
    };

    socket.onclose = () => console.log("WebSocket disconnected");
    socket.onerror = (err) => console.error("WebSocket error:", err);
    // ------------------------------------------------------------------

    // Load initial data
    loadEmployees();
    loadAllLeaves();
    loadDepartments();

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

// Load all employees
async function loadEmployees() {
    try {
        const employeesData = await api.getAllEmployees();
        const tbody = document.getElementById('employeesTableBody');

        // Convert dictionary to array if needed
        const employees = Array.isArray(employeesData)
            ? employeesData
            : Object.values(employeesData || {});

        if (!employees || employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No employees found</td></tr>';
            return;
        }

        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.userName || '-'}</td>
                <td>${emp.empName || '-'}</td>
                <td>${emp.empAge || '-'}</td>
                <td>$${emp.empSalary ? emp.empSalary.toFixed(2) : '-'}</td>
                <td>${emp.departId || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="openEditEmployeeModal('${emp.userName}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteEmployee('${emp.userName}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('employeesTableBody').innerHTML =
            `<tr><td colspan="6" class="error">Error: ${error.message}</td></tr>`;
    }
}

// Register employee
function setupFormHandlers() {
    const registerForm = document.getElementById('registerEmployeeForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultDiv = document.getElementById('registerResult');

            const employeeData = {
                empName: document.getElementById('empName').value,
                empAge: parseInt(document.getElementById('empAge').value),
                empSalary: parseFloat(document.getElementById('empSalary').value),
                departId: document.getElementById('empDepartId').value
            };

            try {
                const result = await api.registerEmployee(employeeData);
                resultDiv.innerHTML = `
                    <div class="success-message">
                        <strong>Success!</strong> Employee registered successfully.<br>
                        <strong>Username:</strong> ${result.username}<br>
                        <strong>Password:</strong> ${result.password}
                    </div>
                `;
                registerForm.reset();
                loadEmployees();
                showSuccess('Employee registered successfully');
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
                showError(error.message);
            }
        });
    }

    // Edit employee form
    const editForm = document.getElementById('editEmployeeForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('editEmployeeUsername').value;
            const updateData = {};

            const empName = document.getElementById('editEmpName').value;
            const empAge = document.getElementById('editEmpAge').value;
            const empSalary = document.getElementById('editEmpSalary').value;
            const departId = document.getElementById('editEmpDepartId').value;

            if (empName) updateData.empName = empName;
            if (empAge) updateData.empAge = parseInt(empAge);
            if (empSalary) updateData.empSalary = parseFloat(empSalary);
            if (departId) updateData.departId = departId;

            try {
                await api.updateEmployee(username, updateData);
                closeEditEmployeeModal();
                loadEmployees();
                showSuccess('Employee updated successfully');
            } catch (error) {
                showError(error.message);
            }
        });
    }

    // Create department form
    const createDeptForm = document.getElementById('createDepartmentForm');
    if (createDeptForm) {
        createDeptForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const resultDiv = document.getElementById('createDepartmentResult');

            const departmentData = {
                departId: document.getElementById('departId').value,
                departName: document.getElementById('departName').value
            };

            try {
                await api.createDepartment(departmentData);
                resultDiv.innerHTML = '<div class="success-message">Department created successfully</div>';
                createDeptForm.reset();
                loadDepartments();
                showSuccess('Department created successfully');
            } catch (error) {
                resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
                showError(error.message);
            }
        });
    }

    // Edit department form
    const editDeptForm = document.getElementById('editDepartmentForm');
    if (editDeptForm) {
        editDeptForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const departId = document.getElementById('editDepartmentId').value;
            const updateData = {};

            const departName = document.getElementById('editDepartName').value;
            if (departName) updateData.departName = departName;

            try {
                await api.updateDepartment(departId, updateData);
                closeEditDepartmentModal();
                loadDepartments();
                showSuccess('Department updated successfully');
            } catch (error) {
                showError(error.message);
            }
        });
    }
}

// Delete employee
async function deleteEmployee(username) {
    if (!confirm(`Are you sure you want to delete employee ${username}?`)) {
        return;
    }

    try {
        await api.deleteEmployee(username);
        loadEmployees();
        showSuccess('Employee deleted successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Open edit employee modal
async function openEditEmployeeModal(username) {
    try {
        const employee = await api.getEmployee(username);
        document.getElementById('editEmployeeUsername').value = employee.userName;
        document.getElementById('editEmpName').value = employee.empName || '';
        document.getElementById('editEmpAge').value = employee.empAge || '';
        document.getElementById('editEmpSalary').value = employee.empSalary || '';
        document.getElementById('editEmpDepartId').value = employee.departId || '';
        document.getElementById('editEmployeeModal').style.display = 'block';
    } catch (error) {
        showError(error.message);
    }
}

// Close edit employee modal
function closeEditEmployeeModal() {
    document.getElementById('editEmployeeModal').style.display = 'none';
}

// Load all leaves
async function loadAllLeaves() {
    try {
        const leavesData = await api.getAllLeaves();
        const tbody = document.getElementById('leavesTableBody');

        // Convert dictionary to array if needed
        const leaves = Array.isArray(leavesData)
            ? leavesData
            : Object.values(leavesData || {});

        if (!leaves || leaves.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="no-data">No leave requests found</td></tr>';
            return;
        }

        tbody.innerHTML = leaves.map(leave => `
            <tr>
                <td>${leave.leave_id || '-'}</td>
                <td>${leave.userName || '-'}</td>
                <td>${leave.Leave_type || '-'}</td>
                <td>${formatDate(leave.start_date)}</td>
                <td>${formatDate(leave.end_date)}</td>
                <td>${leave.reason || '-'}</td>
                <td><span class="status-badge status-${leave.status}">${leave.status || 'pending'}</span></td>
                <td>
                    ${leave.status === 'pending' ? `
                        <button class="btn btn-sm btn-success" onclick="approveLeave('${leave.leave_id}')">Approve</button>
                        <button class="btn btn-sm btn-danger" onclick="rejectLeave('${leave.leave_id}')">Reject</button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('leavesTableBody').innerHTML =
            `<tr><td colspan="8" class="error">Error: ${error.message}</td></tr>`;
    }
}

// Approve leave
async function approveLeave(leaveId) {
    try {
        await api.approveLeave(leaveId);
        // Mark this leave as seen in notifications
        if (typeof window.seenLeaveIds !== 'undefined') {
            window.seenLeaveIds.add(leaveId);
        }
        loadAllLeaves();
        // Reload notifications
        if (typeof window.loadNotifications === 'function') {
            await window.loadNotifications();
        }
        showSuccess('Leave approved successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Reject leave
async function rejectLeave(leaveId) {
    if (!confirm('Are you sure you want to reject this leave request?')) {
        return;
    }

    try {
        await api.rejectLeave(leaveId);
        // Mark this leave as seen in notifications
        if (typeof window.seenLeaveIds !== 'undefined') {
            window.seenLeaveIds.add(leaveId);
        }
        loadAllLeaves();
        // Reload notifications
        if (typeof window.loadNotifications === 'function') {
            await window.loadNotifications();
        }
        showSuccess('Leave rejected');
    } catch (error) {
        showError(error.message);
    }
}

// Load departments
async function loadDepartments() {
    try {
        const departmentsData = await api.getAllDepartments();
        const tbody = document.getElementById('departmentsTableBody');

        // Convert dictionary to array if needed
        const departments = Array.isArray(departmentsData)
            ? departmentsData
            : Object.values(departmentsData || {});

        if (!departments || departments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="no-data">No departments found</td></tr>';
            return;
        }

        tbody.innerHTML = departments.map(dept => `
            <tr>
                <td>${dept.departId || '-'}</td>
                <td>${dept.departName || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="openEditDepartmentModal('${dept.departId}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteDepartment('${dept.departId}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        document.getElementById('departmentsTableBody').innerHTML =
            `<tr><td colspan="3" class="error">Error: ${error.message}</td></tr>`;
    }
}

// Open edit department modal
async function openEditDepartmentModal(departId) {
    try {
        const department = await api.getDepartment(departId);
        document.getElementById('editDepartmentId').value = department.departId;
        document.getElementById('editDepartName').value = department.departName || '';
        document.getElementById('editDepartmentModal').style.display = 'block';
    } catch (error) {
        showError(error.message);
    }
}

// Close edit department modal
function closeEditDepartmentModal() {
    document.getElementById('editDepartmentModal').style.display = 'none';
}

// Delete department
async function deleteDepartment(departId) {
    if (!confirm(`Are you sure you want to delete department ${departId}?`)) {
        return;
    }

    try {
        await api.deleteDepartment(departId);
        loadDepartments();
        showSuccess('Department deleted successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Simple modal helpers (admin.html uses these)
function showEmployeeModal() {
    const modal = document.getElementById('employeeModal');
    if (modal) modal.style.display = 'block';
}

function showDepartmentModal() {
    const modal = document.getElementById('departmentModal');
    if (modal) modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function (event) {
    const employeeModal = document.getElementById('employeeModal');
    const departmentModal = document.getElementById('departmentModal');
    const editEmployeeModal = document.getElementById('editEmployeeModal');
    const editDepartmentModal = document.getElementById('editDepartmentModal');

    if (event.target === employeeModal) {
        employeeModal.style.display = 'none';
    }
    if (event.target === departmentModal) {
        departmentModal.style.display = 'none';
    }
    if (event.target === editEmployeeModal) {
        editEmployeeModal.style.display = 'none';
    }
    if (event.target === editDepartmentModal) {
        editDepartmentModal.style.display = 'none';
    }
}
