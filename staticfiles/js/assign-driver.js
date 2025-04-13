document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".assign-btn");

  buttons.forEach(button => {
      button.addEventListener("click", function () {
        showConfirmationPopup();
      });
  });
});

// Show Confirmation Popup
function showConfirmationPopup() {
  document.getElementById("confirmation-popup").style.display = "flex";
}

// Close Confirmation Popup
function closeConfirmationPopup() {
  document.getElementById("confirmation-popup").style.display = "none";
}

let driverID = null;

function storeDriverID(button){
  driverID = button.dataset.id;
}

function processTheRequests() {
    const urlParams = new URLSearchParams(window.location.search);
    const requestID = urlParams.get('requestID');
      // Show Sucessful Popup
    closeConfirmationPopup();
    fetch("assign_driver/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),  // CSRF token for security
        },
        body: JSON.stringify({ driverID: driverID, requestID:requestID}),
    })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            document.getElementById("successful-popup").style.display = "flex"; // Show success popup
        } else {
            alert("⚠️ " + data.message);
        }
    })
        .catch(error => console.error("Error:", error));

    }

function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

function closeTrackingPopup() {
  // Close Sucessful Popup
  document.getElementById("successful-popup").style.display = "none";
}

