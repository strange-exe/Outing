// js/student.js
document.addEventListener('DOMContentLoaded', () => {
    redirectToLoginIfNotLoggedIn();
    loadStudentData();
});

document.getElementById('logout-button').addEventListener('click', logout);

async function loadStudentData() {
    const studentId = getStudentId();
    const detailsCard = document.getElementById('student-details-card');
    const outingCard = document.getElementById('outing-control-card');

    try {
        const response = await fetch(`${API_BASE_URL}/student?sid=${studentId}`, {
            headers: { /* 'Authorization': `Bearer ${getAuthToken()}` // Add this for protected routes */ }
        });
        const data = await response.json();

        // Populate student details
        const { details, on_outing } = data;
        detailsCard.innerHTML = `
            <h4>${details.name}</h4>
            <p><b>Course:</b> ${details.course}</p>
            <p><b>Branch:</b> ${details.branch}</p>
            <p><b>Semester:</b> ${details.semester}</p>
            <p><b>Hostel:</b> ${details.hostel}</p>
            <a href="history.html" class="btn btn-outline-secondary w-100">📜 View History</a>`;

        // Populate outing controls
        if (on_outing) {
            outingCard.innerHTML = `
                <h5 class="mb-3">You are currently OUTSIDE</h5>
                <button id="return-button" class="btn btn-danger w-100">✅ Mark Return</button>`;
            document.getElementById('return-button').addEventListener('click', markReturn);
        } else {
            outingCard.innerHTML = `
                <h5 class="mb-3">Start a new outing</h5>
                <form id="outing-form">
                    <input name="reason" class="form-control mb-3" placeholder="Reason for outing" required>
                    <button type="submit" class="btn btn-primary w-100">🚶 Start Outing</button>
                </form>`;
            document.getElementById('outing-form').addEventListener('submit', startOuting);
        }
    } catch (error) {
        detailsCard.innerHTML = 'Could not load student data.';
        outingCard.innerHTML = '';
    }
}

async function startOuting(e) {
    e.preventDefault();
    const reason = e.target.elements.reason.value;
    await fetch(`${API_BASE_URL}/student?sid=${getStudentId()}&action=start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
    });
    loadStudentData(); // Refresh the page content
}

async function markReturn() {
    await fetch(`${API_BASE_URL}/student?sid=${getStudentId()}&action=return`, {
        method: 'POST'
    });
    loadStudentData(); // Refresh the page content
}