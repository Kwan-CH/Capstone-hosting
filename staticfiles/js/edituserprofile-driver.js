// document.addEventListener("DOMContentLoaded", function () {
//   document.querySelector(".submit").addEventListener("click", function (event) {
//       event.preventDefault();
//       driver_editProfile_ConfirmationPopup(); // Show confirmation popup first
//   });
// });

// Show Confirmation Popup
function driver_editProfile_ConfirmationPopup() {
  document.getElementById("driver-editProfile-confirmation-popup").style.display = "flex";
}

// Close Confirmation Popup
function driver_editProfile_close_ConfirmationPopup() {
  document.getElementById("driver-editProfile-confirmation-popup").style.display = "none";
}

// Show Sucessful Popup 
function driver_editProfile_show_SucessfulPopup() {
  driver_editProfile_close_ConfirmationPopup(); 
  document.getElementById("driver-editProfile-sucessful-popup").style.display = "flex";
}


// Submit Form
function driver_editProfile_submitForm() {
  document.getElementById("editProfileForm").submit(); //submit form and validate first before show successful popup
}
