// js/auth.js
function saveAuthData(data) {
    localStorage.setItem('authToken', data.token);
    localStorage.setItem('studentId', data.sid);
}

function getAuthToken() {
    return localStorage.getItem('authToken');
}

function getStudentId() {
    return localStorage.getItem('studentId');
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('studentId');
    window.location.href = 'login.html';
}

function redirectToLoginIfNotLoggedIn() {
    if (!getAuthToken()) {
        window.location.href = 'login.html';
    }
}