// document.addEventListener("DOMContentLoaded", function () {
//   document.querySelector(".submit").addEventListener("click", function (event) {
//     event.preventDefault();
//     customer_editPass_ConfirmationPopup(); // Show confirmation popup first
//   });
// });

// Show Confirmation Popup
function customer_editPass_ConfirmationPopup() {
  document.getElementById("customer-editPass-confirmation-popup").style.display = "flex";
}

// Close Confirmation Popup
function customer_editPass_close_ConfirmationPopup() {
  document.getElementById("customer-editPass-confirmation-popup").style.display = "none";
}

// Show Sucessful Popup
function customer_editPass_show_SucessfulPopup() {
  customer_editPass_close_ConfirmationPopup();
  document.getElementById("customer-editPass-sucessful-popup").style.display = "flex";
}

// Submit Form
function customer_editPass_submitForm() {
  document.getElementById("editPasswordForm").submit(); //submit form and validate first before show successful popup
}

