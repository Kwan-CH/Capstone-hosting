document.addEventListener("DOMContentLoaded", function () {
  document.querySelector(".submit").addEventListener("click", function (event) {
      event.preventDefault();
      showResetPasswordPopup(); 
  });
});

// Show Reset Password Email Popup
function showResetPasswordPopup() {
  document.getElementById("reset-password-popup").style.display = "flex";
}

// Close Popup
function closeResetPasswordPopup(){
  document.getElementById("reset-password-popup").style.display = "none";
    window.location.href = "/login/";
}