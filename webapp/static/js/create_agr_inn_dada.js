$("#client_inn_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#client_inn_form").val(suggestion.data.inn);
    }
});
$("#seller_inn1_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#seller_inn1_form").val(suggestion.data.inn);
    }
});
$("#seller_inn2_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#seller_inn2_form").val(suggestion.data.inn);
    }
});
$("#seller_inn3_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#seller_inn3_form").val(suggestion.data.inn);
    }
});
$("#seller_inn4_form").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#seller_inn4_form").val(suggestion.data.inn);
    }
});