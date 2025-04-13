// document.addEventListener("DOMContentLoaded", function () {
//   document.querySelector(".submit").addEventListener("click", function (event) {
//       event.preventDefault();
//       addNewConfirmationPopup(); // Show confirmation popup first
//   });
// });

// Show Confirmation Popup
function addNew_ConfirmationPopup() {
  document.getElementById("addNew-confirmation-popup").style.display = "flex";
}

// Close Confirmation Popup
function addNew_close_ConfirmationPopup() {
  document.getElementById("addNew-confirmation-popup").style.display = "none";
}

// Show Sucessful Popup
function addNew_show_SucessfulPopup() {
  addNew_close_ConfirmationPopup();
  document.getElementById("addNew-sucessful-popup").style.display = "flex";
}
