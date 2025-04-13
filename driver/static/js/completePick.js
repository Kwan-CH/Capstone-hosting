document.addEventListener("DOMContentLoaded", function () {
    // Attach event listeners to all "Completed" buttons
    document.querySelectorAll(".completed-button").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default form submission (if any)
            showConfirmationPopup(); // Show confirmation popup instead
        });
    });
});

// Show Confirmation Popup
function showConfirmationPopup() {
    document.getElementById("proceed-popup").style.display = "flex";
}

// Close Confirmation Popup
function closeConfirmationPopup() {
    document.getElementById("proceed-popup").style.display = "none";
}

// Function to get CSRF Token for security
function getCSRFToken() {
    // return document.querySelector('[name=csrfmiddlewaretoken]').value;
    return document.getElementById("csrf_token")?.value || "";
}

// Show Tracking Number Popup After Confirmation
function showTrackingPopup() {
    closeConfirmationPopup();

    let selectedRequests = [];
    document.querySelectorAll(".pickup-checkbox:checked").forEach(checkbox => {
        let pickupContainer = checkbox.closest(".pickup-container");
        let requestId = pickupContainer.dataset.requestId;  // Get request ID from data attribute
        if (requestId) {
            selectedRequests.push(requestId);
        }
    });

    if (selectedRequests.length === 0) {
        alert("No requests selected!");
        return;
    }

    console.log("Selected Requests:", selectedRequests);

    // Send data to Django view via Fetch API
    fetch("/driver/update_complete_status/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()  // Ensure CSRF protection
        },
        body: JSON.stringify({ request_ids: selectedRequests })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("greatjob-popup").style.display = "flex"; // Show success popup
            } else {
                alert("Failed to update status. Please try again.");
            }
        })
        .catch(error => console.error("Error:", error));
    // document.getElementById("greatjob-popup").style.display = "flex";
}


// Close Tracking Popup
function closeTrackingPopup() {
    document.getElementById("greatjob-popup").style.display = "none";
    location.reload();
}


document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = document.querySelectorAll(".pickup-checkbox");

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            const parentContainer = this.closest(".pickup-container");
            if (this.checked) {
                parentContainer.classList.add("checked");
            } else {
                parentContainer.classList.remove("checked");
            }

            updateCompletedCount();
        });
    });

    const pickupContainers = document.querySelectorAll(".pickup-container");

    pickupContainers.forEach(container => {
        container.addEventListener("click", function (event) {
            // Ignore clicks on the checkbox itself to avoid double toggling
            if (event.target.classList.contains("pickup-checkbox")) {
                return;
            }

            const checkbox = container.querySelector(".pickup-checkbox");
            checkbox.checked = !checkbox.checked; // Toggle checkbox state

            // ✅ Call function to update the "Completed" button count
            updateCompletedCount();
        });
    });
});

function updateCompletedCount() {
    let checkboxes = document.querySelectorAll(".pickup-checkbox:checked");
    let completedButton = document.getElementById("completedButton");
    let count = checkboxes.length;

    if (count > 0) {
        completedButton.textContent = `Completed (${count})`;
    } else {
        completedButton.textContent = "Completed";
    }
}
