var fmsUnit = document.getElementById('fms_unit');
$("#input1").suggestions({
    token: suggestionsToken,
    type: "PARTY",
    /* Вызывается, когда пользователь выбирает одну из подсказок */
    onSelect: function(suggestion) {
        var loadingIndicator = document.getElementById('loading-indicator');
        // Проверяем значение suggestion.data.inn
        if (suggestion.data.inn.length === 12) {
            // Если длина ИНН равна 12, то:
            // Показываем индикатор загрузки
            if (loadingIndicator) {
                loadingIndicator.style.display = 'block';
            }

            $.ajax({
            url: './check_inn_indiv', // URL вашего серверного обработчика
            type: 'POST',
            data: {
                inn: suggestion.data.inn,
                }, // Отправляем ИНН на сервер
            success: function(response) {
                // Если на сервере найдены данные в БД, заполняем поля из ответа
                if (response.director_inn) {
                    $("#inputFiz1").val(response.director_inn);
                    $("#inputFiz3").val(response.passport_series);
                    $("#inputFiz4").val(response.passport_id);
                    $("#inputFiz5").val(response.issued_by);
                    $("#inputFiz6").val(response.issued_when);
                    $("#inputFiz7").val(response.department_code);
                    $("#inputFiz8").val(response.place_of_birth);
                    $("#inputFiz9").val(response.date_of_birth);
                    $("#inputFiz10").val(response.address_reg);
                    if (fmsUnit) {
                        fmsUnit.style.display = 'block';
                    }
                } else {
                    // Если ключ director_inn отсутствует в ответе, используем данные из suggestion.data
                    $("#inputFiz1").val(suggestion.data.inn);
                }
                $("#input1").val("");
                $("#inputFiz2").val(response.director_name);
                $("#inputFiz11").val(response.today);

                // Скрываем кнопку автозаполнения
                var autofillButtonFiz = document.getElementById('autofillButtonFiz');
                if (autofillButtonFiz) {
                    autofillButtonFiz.style.display = 'none';
                }

                // Скрываем индикатор загрузки после завершения AJAX-запроса
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }
            },
            error: function(response) {
                // Если не удалось связаться с БД или не найдены данные, используем API
                $("#inputFiz1").val(suggestion.data.inn);
                $("#input1").val("");
                // Скрываем индикатор загрузки при ошибке
                if (loadingIndicator) {
                    loadingIndicator.style.display = 'none';
                }
            }
        });
        } else {

            // Показываем индикатор загрузки
            if (loadingIndicator) {
                loadingIndicator.style.display = 'block';
            }

            $.ajax({
                url: './check_inn', // URL вашего серверного обработчика
                type: 'POST',
                data: {
                    inn: suggestion.data.inn,
                    director_name: suggestion.data.management.name,
                    director_position: suggestion.data.management.post
                }, // Отправляем ИНН на сервер
                success: function(response) {
                    // Если на сервере найдены данные в БД, заполняем поля из ответа
                    if (response.company_inn) {
                        $("#input1").val(response.company_inn);
                        $("#input2").val(response.company_name);
                        $("#input3").val(response.company_ogrn);
                        $("#input4").val(response.company_address);
                        $("#input5").val(response.company_phone);
                        $("#input6").val(response.signatory_name);
                        $("#input7").val(response.signatory_position);
                        $("#input8").val(response.signatory_basis);
                    } else {
                        // Если ключ company_inn отсутствует в ответе, используем данные из suggestion.data
                        $("#input1").val(suggestion.data.inn);
                        $("#input2").val(suggestion.data.name.full_with_opf);
                        $("#input3").val(suggestion.data.ogrn);
                        $("#input4").val(suggestion.data.address.unrestricted_value);
                        $("#input6").val(response.dir_name);
                        $("#input7").val(response.dir_post);
                        $("#input8").val("Устава");
                    }
                    $("#input9").val(response.today);

                    // Идентификаторы полей, которые нужно показать
                    var fieldIds = ['name_company', 'ogrn_company', 'address_company', 'phone_company',
                                    'director_name', 'director_position', 'director_basis', 'date_today_company'];

                    fieldIds.forEach(function(id) {
                        var field = document.getElementById(id);
                        if (field) {
                            field.style.display = 'block';
                        }
                    });

                    // Скрываем индикатор загрузки после завершения AJAX-запроса
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                },
                error: function(response) {
                    // Если не удалось связаться с БД или не найдены данные, используем API
                    $("#input1").val(suggestion.data.inn);
                    $("#input2").val(suggestion.data.name.full_with_opf);
                    $("#input3").val(suggestion.data.ogrn);
                    $("#input4").val(suggestion.data.address.unrestricted_value);
                    $("#input6").val(response.dir_name);
                    $("#input7").val(response.dir_post);
                    $("#input8").val("Устава");
                    $("#input9").val(response.today);

                    fieldIds.forEach(function(id) {
                        var field = document.getElementById(id);
                        if (field) {
                            field.style.display = 'block';
                        }
                    });

                    // Скрываем индикатор загрузки при ошибке
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                }
            });
        }
    }
});