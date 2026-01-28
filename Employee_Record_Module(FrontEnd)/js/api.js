// API Service Layer
class APIService {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}, retries = 1) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            credentials: 'include', // Important for cookies
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Add Authorization header if token exists in localStorage (fallback if cookies don't work)
        const token = localStorage.getItem('access_token');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            // Handle non-JSON responses
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                // If 204 No Content, text is empty
                data = text ? { message: text } : {};
            }

            if (!response.ok) {
                // Determine error message
                const msg = data.detail || data.message || `Error: ${response.status} ${response.statusText}`;
                throw new Error(msg);
            }

            return data;
        } catch (error) {
            // Retry logic for network errors
            if ((error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) && retries > 0) {
                console.warn(`Request to ${url} failed, retrying... (${retries} attempts left)`);
                await new Promise(res => setTimeout(res, 500)); // Wait 500ms
                return this.request(endpoint, options, retries - 1);
            }

            // Better error handling for network issues
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Cannot connect to server. Make sure the backend is running on http://127.0.0.1:8000');
            }
            throw error;
        }
    }

    // Auth endpoints
    async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ userName: username, password }),
        });
    }

    async logout() {
        return this.request('/auth/logout', {
            method: 'POST',
        });
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Employee endpoints
    async getAllEmployees() {
        return this.request('/employee/');
    }

    async getEmployee(username) {
        return this.request(`/employee/${username}`);
    }

    async registerEmployee(employeeData) {
        return this.request('/employee/register', {
            method: 'POST',
            body: JSON.stringify(employeeData),
        });
    }

    async updateEmployee(username, employeeData) {
        return this.request(`/employee/${username}`, {
            method: 'PUT',
            body: JSON.stringify(employeeData),
        });
    }

    async deleteEmployee(username) {
        return this.request(`/employee/${username}`, {
            method: 'DELETE',
        });
    }

    // Leave endpoints
    async getAllLeaves() {
        return this.request('/leave/');
    }

    async getLeave(leaveId) {
        return this.request(`/leave/${leaveId}`);
    }

    async getMyLeaves() {
        return this.request('/leave/my');
    }

    async applyLeave(leaveData) {
        return this.request('/leave/', {
            method: 'POST',
            body: JSON.stringify(leaveData),
        });
    }

    async updateLeave(leaveId, leaveData) {
        return this.request(`/leave/${leaveId}`, {
            method: 'PUT',
            body: JSON.stringify(leaveData),
        });
    }

    async deleteLeave(leaveId) {
        return this.request(`/leave/${leaveId}`, {
            method: 'DELETE',
        });
    }

    async approveLeave(leaveId) {
        return this.request(`/leave/approve/${leaveId}`, {
            method: 'PUT',
        });
    }

    async rejectLeave(leaveId) {
        return this.request(`/leave/reject/${leaveId}`, {
            method: 'PUT',
        });
    }

    // Department endpoints
    async getAllDepartments() {
        return this.request('/department/');
    }

    async getDepartment(departId) {
        return this.request(`/department/${departId}`);
    }

    async createDepartment(departmentData) {
        return this.request('/department/', {
            method: 'POST',
            body: JSON.stringify(departmentData),
        });
    }

    async updateDepartment(departId, departmentData) {
        return this.request(`/department/${departId}`, {
            method: 'PUT',
            body: JSON.stringify(departmentData),
        });
    }

    async deleteDepartment(departId) {
        return this.request(`/department/${departId}`, {
            method: 'DELETE',
        });
    }
}

// Create API instance
const api = new APIService(API_BASE_URL);
