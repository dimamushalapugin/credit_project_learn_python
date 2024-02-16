var socket = io.connect('http://' + document.domain + ':' + location.port);
document.getElementById('users-table').style.display = 'none';
    function toggleTableVisibility() {
        var checkbox = document.getElementById('flexSwitchCheckDefault');
        var usersTable = document.getElementById('users-table');

        if (checkbox.checked) {
            usersTable.style.display = 'block';
        } else {
            usersTable.style.display = 'none';
        }
    }