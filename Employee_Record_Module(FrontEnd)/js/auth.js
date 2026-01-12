// Authentication Logic
let currentTabUser = null; // Track current user in this tab

document.addEventListener('DOMContentLoaded', async () => {
    // Check if we're on login page
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const errorMessage = document.getElementById('errorMessage');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            errorMessage.classList.remove('show');
            errorMessage.textContent = '';

            try {
                // Login and get user info from response
                const loginResponse = await api.login(username, password);
                
                // Use user info from login response (no need to call /auth/me)
                const userInfo = {
                    userName: loginResponse.userName,
                    role: loginResponse.role
                };
                
                // Store token in localStorage (fallback if cookies don't work)
                if (loginResponse.token) {
                    localStorage.setItem('access_token', loginResponse.token);
                }
                
                // Store user info in localStorage with username key to avoid conflicts across tabs
                localStorage.setItem(`userInfo_${userInfo.userName}`, JSON.stringify(userInfo));
                sessionStorage.setItem('userInfo', JSON.stringify(userInfo));
                sessionStorage.setItem('currentUserName', userInfo.userName);
                
                // Set a flag to indicate a new login (for other tabs to detect)
                localStorage.setItem('lastLoginUser', userInfo.userName);
                localStorage.setItem('lastLoginTime', Date.now().toString());
                
                // Small delay to ensure cookie is set
                await new Promise(resolve => setTimeout(resolve, 200));
                
                // Redirect based on role
                if (userInfo.role === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'employee.html';
                }
            } catch (error) {
                errorMessage.textContent = error.message || 'Login failed. Please check your credentials.';
                errorMessage.classList.add('show');
            }
        });
    } else {
        // On dashboard pages, check authentication
        await checkAuth();
        
        // Set up listener for storage changes (detect login/logout in other tabs)
        setupStorageListener();
    }
});

// Listen for storage changes from other tabs
function setupStorageListener() {
    window.addEventListener('storage', async (e) => {
        // Check if it's a login/logout event
        if (e.key === 'lastLoginUser' || e.key === 'lastLoginTime' || e.key === 'access_token') {
            // Wait a bit for storage to update
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Check current user in this tab
            const currentUserName = sessionStorage.getItem('currentUserName');
            const lastLoginUser = localStorage.getItem('lastLoginUser');
            
            // If another tab logged in as a different user, reload this tab
            if (lastLoginUser && currentUserName && lastLoginUser !== currentUserName) {
                // Different user logged in, reload to switch to their view
                window.location.reload();
            } else if (e.key === 'access_token' && e.oldValue && !e.newValue) {
                // Token was removed (logout in another tab)
                if (currentUserName) {
                    // Clear this tab's session and redirect to login
                    const userName = sessionStorage.getItem('currentUserName');
                    if (userName) {
                        localStorage.removeItem(`userInfo_${userName}`);
                    }
                    sessionStorage.removeItem('userInfo');
                    sessionStorage.removeItem('currentUserName');
                    localStorage.removeItem('access_token');
                    window.location.href = 'index.html';
                }
            } else if (lastLoginUser && !currentUserName) {
                // Another tab logged in, but this tab has no user - reload
                window.location.reload();
            }
        }
    });
    
    // Also check periodically for changes (in case storage event doesn't fire)
    setInterval(async () => {
        const currentUserName = sessionStorage.getItem('currentUserName');
        const lastLoginUser = localStorage.getItem('lastLoginUser');
        
        // If another tab logged in as different user
        if (lastLoginUser && currentUserName && lastLoginUser !== currentUserName) {
            // Verify the current user is still valid
            try {
                const currentUser = await api.getCurrentUser();
                if (currentUser && currentUser.userName !== currentUserName) {
                    // Different user is now logged in, reload
                    window.location.reload();
                }
            } catch (error) {
                // Current user is invalid, check if new user is logged in
                if (lastLoginUser) {
                    window.location.reload();
                }
            }
        }
    }, 2000); // Check every 2 seconds
}

// Logout function
async function logout() {
    try {
        // Clear all storage
        const currentUserName = sessionStorage.getItem('currentUserName');
        if (currentUserName) {
            localStorage.removeItem(`userInfo_${currentUserName}`);
        }
        sessionStorage.removeItem('userInfo');
        sessionStorage.removeItem('currentUserName');
        localStorage.removeItem('access_token');
        
        // Clear login tracking (so other tabs know about logout)
        localStorage.removeItem('lastLoginUser');
        localStorage.removeItem('lastLoginTime');
        
        await api.logout();
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Logout error:', error);
        // Clear all storage even if logout fails
        const currentUserName = sessionStorage.getItem('currentUserName');
        if (currentUserName) {
            localStorage.removeItem(`userInfo_${currentUserName}`);
        }
        sessionStorage.removeItem('userInfo');
        sessionStorage.removeItem('currentUserName');
        localStorage.removeItem('access_token');
        
        // Clear login tracking
        localStorage.removeItem('lastLoginUser');
        localStorage.removeItem('lastLoginTime');
        
        // Still redirect even if logout fails
        window.location.href = 'index.html';
    }
}

// Check authentication and role on page load
async function checkAuth() {
    // First, try to get user info from sessionStorage (set during login)
    let userInfo = null;
    const currentUserName = sessionStorage.getItem('currentUserName');
    
    // Try to get from localStorage first (using username key to avoid tab conflicts)
    if (currentUserName) {
        const storedUserInfo = localStorage.getItem(`userInfo_${currentUserName}`);
        if (storedUserInfo) {
            try {
                userInfo = JSON.parse(storedUserInfo);
            } catch (e) {
                // Invalid stored data, clear it
                localStorage.removeItem(`userInfo_${currentUserName}`);
            }
        }
    }
    
    // Fallback to sessionStorage
    if (!userInfo) {
        const storedUserInfo = sessionStorage.getItem('userInfo');
        if (storedUserInfo) {
            try {
                userInfo = JSON.parse(storedUserInfo);
                // Store in localStorage with username key
                if (userInfo && userInfo.userName) {
                    localStorage.setItem(`userInfo_${userInfo.userName}`, storedUserInfo);
                    sessionStorage.setItem('currentUserName', userInfo.userName);
                }
            } catch (e) {
                // Invalid stored data, clear it
                sessionStorage.removeItem('userInfo');
                localStorage.removeItem('access_token');
            }
        }
    }
    
    // If we have stored user info, use it immediately (don't block on API call)
    if (userInfo) {
        // Update current user display
        updateUserDisplay(userInfo);

        // Check if user is on the correct page based on role
        const currentPage = window.location.pathname.split('/').pop();
        if (userInfo.role === 'admin' && currentPage === 'employee.html') {
            window.location.href = 'admin.html';
            return userInfo;
        } else if (userInfo.role === 'employee' && currentPage === 'admin.html') {
            window.location.href = 'employee.html';
            return userInfo;
        }

        // Verify with backend in background (non-blocking) - don't redirect on failure
        api.getCurrentUser().then(verifiedUser => {
            if (verifiedUser) {
                localStorage.setItem(`userInfo_${verifiedUser.userName}`, JSON.stringify(verifiedUser));
                sessionStorage.setItem('userInfo', JSON.stringify(verifiedUser));
                sessionStorage.setItem('currentUserName', verifiedUser.userName);
                // Update display with verified user info
                updateUserDisplay(verifiedUser);
            }
        }).catch(() => {
            // Verification failed, but don't redirect - user might still be valid
            console.log('Background verification failed, but keeping user session');
        });

        return userInfo;
    }
    
    // No stored info, try to get from API
    try {
        userInfo = await api.getCurrentUser();
        // Store it for future use
        if (userInfo) {
            localStorage.setItem(`userInfo_${userInfo.userName}`, JSON.stringify(userInfo));
            sessionStorage.setItem('userInfo', JSON.stringify(userInfo));
            sessionStorage.setItem('currentUserName', userInfo.userName);
            
            // Update current user display
            updateUserDisplay(userInfo);

            // Check if user is on the correct page based on role
            const currentPage = window.location.pathname.split('/').pop();
            if (userInfo.role === 'admin' && currentPage === 'employee.html') {
                window.location.href = 'admin.html';
            } else if (userInfo.role === 'employee' && currentPage === 'admin.html') {
                window.location.href = 'employee.html';
            }
            
            return userInfo;
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        // API call failed - redirect to login only if we're on a protected page
        const currentPage = window.location.pathname.split('/').pop();
        if (currentPage !== 'index.html') {
            // Clear stored info
            const currentUserName = sessionStorage.getItem('currentUserName');
            if (currentUserName) {
                localStorage.removeItem(`userInfo_${currentUserName}`);
            }
            sessionStorage.removeItem('userInfo');
            sessionStorage.removeItem('currentUserName');
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
        }
        return false;
    }
    
    // No user info at all - redirect to login only if on protected page
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage !== 'index.html') {
        const currentUserName = sessionStorage.getItem('currentUserName');
        if (currentUserName) {
            localStorage.removeItem(`userInfo_${currentUserName}`);
        }
        sessionStorage.removeItem('userInfo');
        sessionStorage.removeItem('currentUserName');
        localStorage.removeItem('access_token');
        window.location.href = 'index.html';
    }
    return false;
}

// Get current user info
async function getCurrentUserInfo() {
    try {
        return await api.getCurrentUser();
    } catch (error) {
        return null;
    }
}

// Update user display with name (for employees) or username (for admin)
async function updateUserDisplay(userInfo) {
    const currentUserSpan = document.getElementById('currentUser');
    if (!currentUserSpan) return;
    
    if (userInfo.role === 'employee') {
        // For employees, fetch and show their actual name
        try {
            const employee = await api.getEmployee(userInfo.userName);
            if (employee && employee.empName) {
                currentUserSpan.textContent = employee.empName;
            } else {
                currentUserSpan.textContent = userInfo.userName;
            }
        } catch (error) {
            // If fetching fails, just show username
            currentUserSpan.textContent = userInfo.userName;
        }
    } else {
        // For admin, show username
        currentUserSpan.textContent = userInfo.userName;
    }
}
