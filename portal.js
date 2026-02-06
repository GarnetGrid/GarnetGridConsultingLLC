// Secure Access Portal Logic (Client-Side Simulation)
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('accessForm');
    const input = document.getElementById('accessCode');
    const msg = document.getElementById('statusMsg');

    // Simple Hash for "Garnet2026" (Not cryptographically secure, but functional for this demo)
    // "Garnet2026"

    const TARGET_HASH = "Garnet2026";

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const code = input.value.trim();

        msg.className = 'status-msg';
        msg.innerText = 'Verifying Credentials...';

        // Simulate Network Delay
        setTimeout(() => {
            if (code === TARGET_HASH) {
                // Success
                msg.classList.add('success');
                msg.innerText = 'ACCESS GRANTED. REDIRECTING...';

                // Set Session
                sessionStorage.setItem('ggc_secure_session', 'true');
                sessionStorage.setItem('ggc_session_id', 'NODE_' + Math.floor(Math.random() * 9000 + 1000));

                setTimeout(() => {
                    window.location.href = 'portal-dashboard.html';
                }, 1000);
            } else {
                // Failure
                msg.classList.add('error');
                msg.innerText = 'ACCESS DENIED: INVALID KEY';
                input.value = '';
                input.focus();
            }
        }, 800);
    });
});
