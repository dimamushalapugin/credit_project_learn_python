var fmsUnit = document.getElementById('fms_unit');
$("#inputFiz7").suggestions({
    token: suggestionsToken,
    type: "FMS_UNIT",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        $("#inputFiz5").val(suggestion.data.name);
        $("#inputFiz7").val(suggestion.data.code);
        if (fmsUnit) {
            fmsUnit.style.display = 'block';
        }
    }
});