$(document).ready(function () {
    $("#inputFiz10").suggestions({
        token: suggestionsToken,
        type: "ADDRESS",
        onSelect: function(suggestion) {
            console.log(suggestion);
        }
    });
});