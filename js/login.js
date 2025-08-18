// js/login.js

// Pre-fill SID from URL if present
const urlParams = new URLSearchParams(window.location.search);
const sidFromUrl = urlParams.get('sid');
if (sidFromUrl) {
    document.querySelector('input[name="sid"]').value = sidFromUrl;
}

document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const alertContainer = document.getElementById('alert-container');

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            saveAuthData(result);
            window.location.href = 'student.html';
        } else {
            alertContainer.innerHTML = `<div class="alert alert-danger">${result.error || 'Login failed.'}</div>`;
        }
    } catch (error) {
        alertContainer.innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
    }
});