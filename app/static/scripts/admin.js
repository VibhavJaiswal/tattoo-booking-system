document.addEventListener("DOMContentLoaded", () => {
    const API_KEY = "12589";
    const API_URL = "/admin/bookings/";

    fetch(API_URL, {
        headers: {
            "x-api-key": API_KEY
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch bookings");
        }
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            renderBookings(data.bookings);
        } else {
            alert("Error loading bookings: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error loading bookings. See console for details.");
    });

    function renderBookings(bookings) {
        const tableBody = document.getElementById("bookingsBody");
        tableBody.innerHTML = "";

        bookings.forEach(booking => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${booking.summary || ""}</td>
                <td>${booking.description || ""}</td>
                <td>${formatDate(booking.start)}</td>
                <td>${formatDate(booking.end)}</td>
                <td>${booking.id || ""}</td>
            `;

            tableBody.appendChild(row);
        });
    }

    function formatDate(isoString) {
        if (!isoString) return "";
        const date = new Date(isoString);
        return date.toLocaleString();
    }
});
