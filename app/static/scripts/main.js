document.addEventListener("DOMContentLoaded", function () {
document.addEventListener("DOMContentLoaded", function () {
console.log("🧠 main.js loaded — checking for #send-button...");
console.log("✅ main.js is running");

document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("send-button");
    console.log("🧪 Button found?", btn);
    const chatContainer = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");

    function appendMessage(sender, message) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

    sendButton.addEventListener("click", async function () {
        console.log("✅ Send button clicked");
        const userInput = chatInput.value.trim();
        if (userInput === "") return;

        appendMessage("user", userInput);
        chatInput.value = "";

        console.log("📤 Sending request to /chat/");

        try {
            const response = await fetch("/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": "12589"
                },
                body: JSON.stringify({ message: userInput })
            });

            const data = await response.json();
            appendMessage("bot", data.reply);
        } catch (error) {
            console.error("❌ Error sending request:", error);
            appendMessage("bot", "Something went wrong.");
        }
    });
    // scripts/main.js
    
    console.log("✅ main.js is running");
    
    async function loadAvailableSlots() {
        try {
            let response = await fetch("/available_slots/", {
                headers: {
                    "x-api-key": "12589"
                }
            });
    
            let data = await response.json();
            if (data.status === "success") {
                const dropdown = document.getElementById("bookingDateTime");
                dropdown.innerHTML = '<option value="">-- Select Available Slot --</option>';
    
                data.available_slots.forEach(slot => {
                    const option = document.createElement("option");
                    option.value = slot.replace(" ", "T");
                    option.textContent = slot;
                    dropdown.appendChild(option);
                });
            } else {
                alert("Failed to load available slots.");
            }
        } catch (error) {
            console.error("Error loading slots:", error);
            alert("Error loading available slots.");
        }
    }
    
    function showError(message) {
        let errorMessage = document.getElementById("errorMessage");
        errorMessage.textContent = message;
        errorMessage.style.display = "block";
        setTimeout(() => {
            errorMessage.style.display = "none";
        }, 5000);
    }
    
    document.getElementById("uploadForm").onsubmit = async function(event) {
        event.preventDefault();
        let fileInput = document.getElementById("fileInput").files[0];
        let bookingDateTime = document.getElementById("bookingDateTime").value;
    
        if (!fileInput || !bookingDateTime) {
            showError("Please select an image and a time slot.");
            return;
        }
    
        let formData = new FormData();
        formData.append("file", fileInput);
        formData.append("bookingDateTime", bookingDateTime);
    
        let submitButton = document.querySelector("button[type='submit']");
        submitButton.disabled = true;
        submitButton.textContent = "Processing...";
    
        document.getElementById("loadingSpinner").style.display = "block";
        document.getElementById("outputImage").style.display = "none";
        document.getElementById("errorMessage").style.display = "none";
    
        try {
            let response = await fetch("/predict/", {
                method: "POST",
                headers: {
                    "x-api-key": "12589"
                },
                body: formData
            });
    
            let result = await response.json();
            document.getElementById("loadingSpinner").style.display = "none";
    
            if (result.status === "error") {
                showError(result.message || "An error occurred.");
                submitButton.disabled = false;
                submitButton.textContent = "Submit";
                return;
            }
    
            if (result.status === "success" && result.detections.length > 0) {
                document.getElementById("tattooStyle").textContent = result.detections[0].tattoo_style;
                document.getElementById("complexityLevel").textContent = result.detections[0].complexity_level;
                document.getElementById("price").textContent = result.detections[0].estimated_price_usd;
                document.getElementById("sessionTime").textContent = result.detections[0].estimated_time_hours;
    
                let bookingLink = document.getElementById("bookingLink");
                bookingLink.href = result.detections[0].booking_link;
                bookingLink.style.display = "block";
    
                if (result.detections[0].event_id) {
                    localStorage.setItem("eventId", result.detections[0].event_id);
                    document.getElementById("cancelButton").style.display = "block";
                }
    
                if (result.image_base64) {
                    document.getElementById("outputImage").src = result.image_base64;
                    document.getElementById("outputImage").style.display = "block";
                } else {
                    showError("No image received from server.");
                }
            } else {
                showError("No tattoos detected or unexpected error.");
            }
        } catch (error) {
            console.error("❌ Fetch error:", error);
            showError("Error processing image. Please try again.");
            document.getElementById("loadingSpinner").style.display = "none";
        }
    
        submitButton.disabled = false;
        submitButton.textContent = "Submit";
    };
    
    async function sendMessage() {
        let userMessage = document.getElementById("chat-input").value.trim();
        if (!userMessage) return;
        let chatMessages = document.getElementById("chat-messages");
        chatMessages.innerHTML += `<div><b>You:</b> ${userMessage}</div>`;
        document.getElementById("chat-input").value = "";
    
        console.log("📤 Sending request to /chat/");
        let response = await fetch("/chat/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "x-api-key": "12589"
            },
            body: JSON.stringify({ "message": userMessage })
        });
    
        let data = await response.json();
        chatMessages.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    async function cancelBooking() {
        let eventId = localStorage.getItem("eventId");
    
        if (!eventId) {
            alert("No appointment found to cancel.");
            return;
        }
    
        let formData = new FormData();
        formData.append("event_id", eventId);
    
        try {
            let response = await fetch("/cancel_booking/", {
                method: "POST",
                headers: {
                    "x-api-key": "12589"
                },
                body: formData
            });
    
            let result = await response.json();
            console.log("Cancel Booking API Response:", result);
    
            if (result.status === "success") {
                alert("Appointment canceled successfully.");
                document.getElementById("cancelButton").style.display = "none";
                document.getElementById("bookingLink").style.display = "none";
                localStorage.removeItem("eventId");
            } else {
                alert("Error: " + result.error);
            }
        } catch (error) {
            alert("Failed to cancel appointment. Please try again.");
        }
    }
    
    // Load available slots when the page loads
    loadAvailableSlots();
    const cancelButton = document.getElementById("cancelButton");
    cancelButton.addEventListener("click", cancelBooking);
});
});
});
