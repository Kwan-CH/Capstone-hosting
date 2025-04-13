document.addEventListener("DOMContentLoaded", function () {
    let selectedReward = null;
    let selectedPoints = 0;
    const rewardBoxes = document.querySelectorAll(".reward-box");
    const redeemButton = document.querySelector(".redeem");
    const confirmationPopup = document.getElementById("confirmation-popup");
    const successfulPopup = document.getElementById("successful-popup");

    rewardBoxes.forEach(box => {
        box.addEventListener("click", function () {
            // Remove previous selection
            rewardBoxes.forEach(b => b.classList.remove("selected"));

            // Highlight the selected reward
            this.classList.add("selected");
            selectedReward = this.getAttribute("data-rewardID");
            selectedPoints = parseInt(this.getAttribute("data-points"));
            console.log(selectedReward)

            // Enable redeem button
            redeemButton.disabled = false;
        });
    });

    redeemButton.addEventListener("click", function () {
        if (selectedReward) {
            confirmationPopup.style.display = "flex";
        }
    });

    // Function to close the confirmation popup
    function closeConfirmationPopup() {
        confirmationPopup.style.display = "none";
    }

    // Function to confirm redemption and send request to backend
    function confirmRedemption() {
        console.log("Entering redeem action")
        confirmationPopup.style.display = "none"; // Close confirmation popup

        fetch("redeem_voucher/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),  // CSRF token for security
            },
            body: JSON.stringify({ reward: selectedReward, points: selectedPoints }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                successfulPopup.style.display = "flex"; // Show success popup
            } else {
                alert("⚠️ " + data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Function to close successful popup
    function closeSuccessfulPopup() {
        console.log("close success pop ")
        successfulPopup.style.display = "none";

        // Reset selection and disable redeem button
        rewardBoxes.forEach(b => b.classList.remove("selected"));
        redeemButton.disabled = true;

        // Reload the page to update points
        window.location.reload();
    }

    // CSRF token retrieval function
    function getCookie(name) {
        console.log("getting cookie")
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

    // Attach functions to global scope for inline HTML event handlers
    window.closeConfirmationPopup = closeConfirmationPopup;
    window.confirmRedemption = confirmRedemption;
    window.closeSuccessfulPopup = closeSuccessfulPopup;
});
