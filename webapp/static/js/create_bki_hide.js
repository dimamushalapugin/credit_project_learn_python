// Идентификаторы полей, которые нужно скрыть
var fieldIds = ['name_company', 'ogrn_company', 'address_company', 'phone_company',
                'director_name', 'director_position', 'director_basis', 'date_today_company', 'fms_unit'];

// Скрываем все поля
fieldIds.forEach(function(id) {
    var field = document.getElementById(id);
    if (field) {
        field.style.display = 'none';
    }
});