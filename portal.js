// Secure Access Portal Logic (Real Auth Implementation)
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const msg = document.getElementById('statusMsg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) return;

        msg.className = 'status-msg';
        msg.innerText = 'Verifying Credentials...';

        try {
            // Prepare OAuth2 form data
            const formData = new URLSearchParams();
            formData.append('username', email); // OAuth2 spec requires 'username' field
            formData.append('password', password);

            const API_BASE = 'http://localhost:8000'; // Update for production
            const response = await fetch(`${API_BASE}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
                credentials: 'include' // Important for cross-origin cookies
            });

            if (response.ok) {
                // Success - Cookie is set by server (HttpOnly)
                msg.classList.add('success');
                msg.innerText = 'ACCESS GRANTED. REDIRECTING...';

                setTimeout(() => {
                    window.location.href = 'portal-dashboard.html';
                }, 1000);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Invalid credentials');
            }
        } catch (error) {
            console.error('Login failed:', error);
            msg.classList.add('error');
            msg.innerText = 'ACCESS DENIED: INVALID CREDENTIALS';
            passwordInput.value = '';
            passwordInput.focus();
        }
    });
});
