document.addEventListener("DOMContentLoaded", () => {
    // IMPORTANT: Replace this with the actual URL you get from Vercel after deploying your API.
    const apiUrl = 'https://your-outing-api.vercel.app/api/history';
    
    // In a real app, you would get the student ID after they log in.
    const studentId = '12345'; 

    const tableBody = document.getElementById('history-body');

    // Fetch data from the API
    fetch(`${apiUrl}?sid=${studentId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(outings => {
            // Clear the "Loading..." message
            tableBody.innerHTML = ''; 

            if (outings.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="3">No outing history found.</td></tr>';
                return;
            }

            // Create a table row for each outing
            outings.forEach(outing => {
                const row = document.createElement('tr');
                
                // Format the dates to be more readable
                const outTime = new Date(outing.time_out).toLocaleString();
                const inTime = outing.time_in ? new Date(outing.time_in).toLocaleString() : "⏳ Not Returned";

                row.innerHTML = `
                    <td>${outing.reason}</td>
                    <td>${outTime}</td>
                    <td>${inTime}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching outing history:', error);
            tableBody.innerHTML = '<tr><td colspan="3" class="text-danger">Could not load history. Please check the API URL in script.js and ensure the backend is running.</td></tr>';
        });
});