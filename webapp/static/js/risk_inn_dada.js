
$("#client_inn_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#client_inn_form").val(suggestion.data.inn);
    }
});
$("#seller_inn_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#seller_inn_form").val(suggestion.data.inn);
    }
});