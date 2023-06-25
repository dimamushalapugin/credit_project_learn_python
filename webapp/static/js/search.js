function searchLeasingContract() {
    // Get the search query entered by the user
    var query = document.getElementById('searchInput').value.toLowerCase();

    // Get all the rows in the table body
    var rows = document.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Loop through each row and check if it matches the search query
    for (var i = 0; i < rows.length; i++) {
        var contractNumber = rows[i].getElementsByTagName('td')[1].innerText.toLowerCase();

        // If the contract number contains the search query, display the row, otherwise hide it
        if (contractNumber.includes(query)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// Add an event listener to the search input field
document.getElementById('searchInput').addEventListener('input', searchLeasingContract);

function searchBank() {
    var query = document.getElementById('searchInput2').value.toLowerCase();

    var rows = document.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (var i = 0; i < rows.length; i++) {
        var nameBank = rows[i].getElementsByTagName('td')[2].innerText.toLowerCase();

        if (nameBank.includes(query)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

document.getElementById('searchInput2').addEventListener('input', searchBank);

function searchCreditContract() {
    var query = document.getElementById('searchInput3').value.toLowerCase();

    var rows = document.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (var i = 0; i < rows.length; i++) {
        var creditContract = rows[i].getElementsByTagName('td')[3].innerText.toLowerCase();

        if (creditContract.includes(query)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

document.getElementById('searchInput3').addEventListener('input', searchCreditContract);