document.addEventListener('DOMContentLoaded', function() {
  var genderButtons = document.querySelectorAll('.select-menu-list button[data-gender]');
  var newcomerButtons = document.querySelectorAll('.select-menu-list button[data-newcomer]');
  var payButtons = document.querySelectorAll('.select-menu-list button[data-paid]');
  var westernButtons = document.querySelectorAll('.select-menu-list button[data-western]');



  var genderContributorTable = document.getElementById('gender-contributor-table');
  var newcomerContributorTable = document.getElementById('newcomer-contributor-table');
  var paidContributorTable = document.getElementById('paid-contributor-table');
  var westernContributorTable = document.getElementById('western-contributor-table');



  var femaleTable = document.getElementById('female-table');
  var maleTable = document.getElementById('male-table');

  var newcomerTable = document.getElementById('newcomer-table');
  var noNewcomerTable = document.getElementById('no-newcomer-table');

  var paidTable = document.getElementById('paid-table');
  var notpaidTable = document.getElementById('no-paid-table');

  var westernTable = document.getElementById('western-table');
  var nowesternTable = document.getElementById('no-western-table');


  var genderSelectMenu = document.querySelector('.select-menu');
  var newcomerSelectMenu = document.querySelector('.newcomer-select');
  var paidSelectMenu = document.querySelector('.paid-select');
  var westernSelectMenu = document.querySelector('.western-select');



  // Set default gender
  genderContributorTable.innerHTML = femaleTable.innerHTML;

  // Set default newcomer
  newcomerContributorTable.innerHTML = newcomerTable.innerHTML;

  // Set default paid
  paidContributorTable.innerHTML = notpaidTable.innerHTML;

  // Set default western
  westernContributorTable.innerHTML = nowesternTable.innerHTML;


  for (var i = 0; i < genderButtons.length; i++) {
    genderButtons[i].addEventListener('click', function(event) {
      var selectedGender = event.target.getAttribute('data-gender');

      if (selectedGender === 'female') {
        genderContributorTable.innerHTML = femaleTable.innerHTML;
      } else {
        genderContributorTable.innerHTML = maleTable.innerHTML;
      }

      // Hide the gender dropdown menu
      event.stopPropagation(); // Prevent event bubbling
    });
  }

  for (var j = 0; j < newcomerButtons.length; j++) {
    newcomerButtons[j].addEventListener('click', function(event) {
      var selectedNewcomer = event.target.getAttribute('data-newcomer');

      if (selectedNewcomer === 'yes') {
        newcomerContributorTable.innerHTML = newcomerTable.innerHTML;
      } else {
        newcomerContributorTable.innerHTML = noNewcomerTable.innerHTML;
      }

      // Hide the newcomer dropdown menu
      event.stopPropagation(); // Prevent event bubbling
    });
  }


  for (var j = 0; j < payButtons.length; j++) {
    payButtons[j].addEventListener('click', function(event) {
      var selectedPaid = event.target.getAttribute('data-paid');

      if (selectedPaid === 'yes') {
        paidContributorTable.innerHTML = paidTable.innerHTML;
      } else {
        paidContributorTable.innerHTML = notpaidTable.innerHTML;
      }

      // Hide the paid dropdown menu
      event.stopPropagation(); // Prevent event bubbling
    });
  }

  for (var j = 0; j < westernButtons.length; j++) {
    westernButtons[j].addEventListener('click', function(event) {
      var selectedWestern = event.target.getAttribute('data-western');

      if (selectedWestern === 'yes') {
        westernContributorTable.innerHTML = nowesternTable.innerHTML;
      } else {
        westernContributorTable.innerHTML = westernTable.innerHTML;
      }

      // Hide the residency dropdown menu
      event.stopPropagation(); // Prevent event bubbling
    });
  }


  // Close the dropdown menus when clicking outside
  document.addEventListener('click', function(event) {
    if (!event.target.classList.contains('select-menu-item') && !event.target.classList.contains('newcomer-select-item')) {
      genderSelectMenu.removeAttribute('open');
      newcomerSelectMenu.removeAttribute('open');
      paidSelectMenu.removeAttribute('open');
      westernSelectMenu.removeAttribute('open');


    }
  });
});
