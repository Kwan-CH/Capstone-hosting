// document.addEventListener("DOMContentLoaded", function () {
//   document.querySelector(".submit").addEventListener("click", function (event) {
//       event.preventDefault();
//       driver_editPass_ConfirmationPopup(); // Show confirmation popup first
//   });
// });

// Show Confirmation Popup
function driver_editPass_ConfirmationPopup() {
  document.getElementById("driver-editPass-confirmation-popup").style.display = "flex";
}

// Close Confirmation Popup
function driver_editPass_close_ConfirmationPopup() {
  document.getElementById("driver-editPass-confirmation-popup").style.display = "none";
}

// Show Sucessful Popup 
function driver_editPass_show_SucessfulPopup() {
  driver_editPass_close_ConfirmationPopup(); 
  document.getElementById("driver-editPass-sucessful-popup").style.display = "flex";
}

// Submit Form
function driver_editPass_submitForm() {
  document.getElementById("editPasswordForm").submit(); //submit form and validate first before show successful popup
}