// Authentication Functions

function toggleForm(e) {
    e.preventDefault();
    document.getElementById('loginForm').classList.toggle('d-none');
    document.getElementById('registerForm').classList.toggle('d-none');
    clearErrors();
}

// Login Form Submission
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginFormElement');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleLogin();
        });
    }

    const registerForm = document.getElementById('registerFormElement');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleRegister();
        });
    }
});

async function handleLogin() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    try {
        errorDiv.classList.add('d-none');
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username.toLowerCase(),
                password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            const errorMsg = error.detail 
                ? (typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail))
                : 'Login failed';
            throw new Error(errorMsg);
        }

        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('currentUser', username);
        
        // Redirect to dashboard
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('d-none');
    }
}

async function handleRegister() {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const errorDiv = document.getElementById('registerError');

    try {
        errorDiv.classList.add('d-none');
        
        // Validate username format
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            throw new Error('Username must be alphanumeric or contain underscores only');
        }

        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username.toLowerCase(),
                email: email.toLowerCase(),
                password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Registration error:', error);
            let errorMsg = 'Registration failed';
            
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMsg = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMsg = error.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
                } else {
                    errorMsg = JSON.stringify(error.detail);
                }
            }
            throw new Error(errorMsg);
        }

        // Show success and switch to login
        alert('Account created successfully! Please login.');
        document.getElementById('registerForm').classList.add('d-none');
        document.getElementById('loginForm').classList.remove('d-none');
        document.getElementById('registerFormElement').reset();
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('d-none');
    }
}

function clearErrors() {
    document.getElementById('loginError').classList.add('d-none');
    document.getElementById('registerError').classList.add('d-none');
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    
    // Call logout endpoint to blacklist token on server (optional)
    fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: getAuthHeaders()
    }).catch(() => {
        // Ignore errors, user is logged out locally regardless
    });
    
    window.location.href = 'index.html';
}
