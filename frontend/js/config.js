// Configuration
const API_URL = 'http://127.0.0.1:9500/api/v1';

let authToken = null;
let currentUser = null;

// Check if user is logged in
function checkAuth() {
    authToken = localStorage.getItem('token');
    currentUser = localStorage.getItem('currentUser');
    
    if (!authToken || !currentUser) {
        window.location.href = 'index.html';
    }
}

// Set auth header
function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    };
}

// API Call Helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: getAuthHeaders()
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (response.status === 401) {
            logout();
            return null;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        throw error;
    }
}
