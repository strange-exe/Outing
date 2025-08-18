// js/register.js
document.getElementById('register-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const alertContainer = document.getElementById('alert-container');

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            alertContainer.innerHTML = `<div class="alert alert-success">Registration successful! Redirecting to login...</div>`;
            setTimeout(() => window.location.href = 'login.html', 2000);
        } else {
            alertContainer.innerHTML = `<div class="alert alert-danger">${result.error || 'Registration failed.'}</div>`;
        }
    } catch (error) {
        alertContainer.innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
    }
});