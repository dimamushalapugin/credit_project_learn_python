var fmsUnit = document.getElementById('fmsUnit');
var passportBy = document.getElementById('inputFiz5');
<!--    после ввода ИНН парсит все данные в дадата и вставляет их в поля-->
        $(document).ready(function() {
            $('#autofillButton').click(function() {
                var data = $('#input1').val();
                $.ajax({
                    url: './autofill',
                    type: 'POST',
                    data: {'data': data},
                    success: function(response) {
                    $('#input2').val(response.data1);
                    $('#input3').val(response.data2);
                    $('#input4').val(response.data3);
                    $('#input5').val(response.data8);
                    $('#input6').val(response.data4);
                    $('#input7').val(response.data5);
                    $('#input8').val(response.data6);
                    $('#input9').val(response.data7);
                }
                });
            });
        });
    <!--при нажатии на кнопку "Скачать заявку ООО "ЛКМБ-РТ"" парсит данные с сайта и скачивается заявка в ворде-->
    $(document).ready(function() {
        $('#submit-button1').click(function() {
            var bkiurLkmb1 = $('#input1').val();
            var bkiurLkmb2 = $('#input2').val();
            var bkiurLkmb3 = $('#input3').val();
            var bkiurLkmb4 = $('#input4').val();
            var bkiurLkmb5 = $('#input5').val();
            var bkiurLkmb6 = $('#input6').val();
            var bkiurLkmb7 = $('#input7').val();
            var bkiurLkmb8 = $('#input8').val();
            var bkiurLkmb9 = $('#input9').val();
            $.ajax({
                url: './submit_form_ur',
                type: 'POST',
                data: {'data': bkiurLkmb1,
                       'data1': bkiurLkmb2,
                       'data2': bkiurLkmb3,
                       'data3': bkiurLkmb4,
                       'data4': bkiurLkmb5,
                       'data5': bkiurLkmb6,
                       'data6': bkiurLkmb7,
                       'data7': bkiurLkmb8,
                       'data8': bkiurLkmb9},
                success: function(response) {
                    // Предполагается, что сервер вернул ссылку на скачивание в переменной response.downloadLink
                    var downloadLink = response.downloadLink;
                    var hrefValue, downloadValue;
                    // Создаем скрытую ссылку для скачивания
                    var link = document.createElement('a');
                    link.href = '/static/temporary/БКИ ' + bkiurLkmb2.replace(/"/g, '') + '.docx';  // Вставляем значение из bkiurLkmb2
                    link.download = 'БКИ ' + bkiurLkmb2.replace(/"/g, '') + '.docx';  // Вставляем значение из bkiurLkmb2

                    if (bkiurLkmb2.length > 110) {
                        hrefValue = '/static/temporary/БКИ _.docx';
                        downloadValue = 'БКИ _.docx';
                    } else {
                        hrefValue = '/static/temporary/БКИ ' + bkiurLkmb2.replace(/"/g, '') + '.docx';
                        downloadValue = 'БКИ ' + bkiurLkmb2.replace(/"/g, '') + '.docx';
                    }

                    // Присваиваем значение href в зависимости от условия
                    link.href = hrefValue;
                    link.download = downloadValue;  // Вставляем значение из bkiurLkmb2

                    document.body.appendChild(link);

                    // Имитируем клик по ссылке для начала скачивания
                    link.click();

                    // Удаляем временную ссылку
                    document.body.removeChild(link);
                }
            });
        });
    });
    <!--не дает странице обновиться при нажатии на кнопку "Скачать заявку ООО "ЛКМБ-РТ""-->
    document.getElementById("submit-button1").addEventListener("click", function(event) {
            event.preventDefault();
        });
    <!--    делает неактивной кнопку "Скачать заявку ООО "ЛКМБ-РТ" при незаполненных данных. Срабатывает каждую секунду-->
        $(document).ready(function() {
        $('#submit-button1').prop('disabled', true);

        setInterval(function() {
            if ($('#input1').val() !== '' && $('#input2').val() !== '' && $('#input3').val() !== ''
            && $('#input4').val() !== '' && $('#input5').val() !== '' && $('#input6').val() !== ''
            && $('#input7').val() !== '' && $('#input8').val() !== '' && $('#input9').val() !== '') {
                $('#submit-button1').prop('disabled', false);
            } else {
                $('#submit-button1').prop('disabled', true);
            }
        }, 1000);
    });

<!--    Скрипты ниже работают по физику-->
    <!--    после ввода ИНН парсит все данные в дадата и вставляет их в поля-->
        $(document).ready(function() {
            $('#autofillButtonFiz').click(function() {
                var fiz1 = $('#inputFiz1').val();
                $.ajax({
                    url: './autofillfiz',
                    type: 'POST',
                    data: {'data': fiz1},
                    success: function(response) {
                    $('#inputFiz2').val(response.data1);
                    $('#inputFiz3').val(response.data2);
                    $('#inputFiz4').val(response.data3);
                    $('#inputFiz5').val(response.data4);
                    $('#inputFiz6').val(response.data5);
                    $('#inputFiz7').val(response.data6);
                    $('#inputFiz8').val(response.data7);
                    $('#inputFiz9').val(response.data8);
                    $('#inputFiz10').val(response.data9);
                    $('#inputFiz11').val(response.data10);
                    if (fmsUnit && passportBy && passportBy.value.trim() !== '') {
                        fmsUnit.style.display = 'block';
                    }
                }
                });
            });
        });

    <!--при нажатии на кнопку "Скачать заявку ООО "ЛКМБ-РТ"" парсит данные с сайта и скачивается заявка в ворде-->
    $(document).ready(function() {
        $('#submit-button_fiz').click(function() {
            var bkifizLkmb1 = $('#inputFiz1').val();
            var bkifizLkmb2 = $('#inputFiz2').val();
            var bkifizLkmb3 = $('#inputFiz3').val();
            var bkifizLkmb4 = $('#inputFiz4').val();
            var bkifizLkmb5 = $('#inputFiz5').val();
            var bkifizLkmb6 = $('#inputFiz6').val();
            var bkifizLkmb7 = $('#inputFiz7').val();
            var bkifizLkmb8 = $('#inputFiz8').val();
            var bkifizLkmb9 = $('#inputFiz9').val();
            var bkifizLkmb10 = $('#inputFiz10').val();
            var bkifizLkmb11 = $('#inputFiz11').val();
            $.ajax({
                url: './submit_form_fiz',
                type: 'POST',
                data: {'data': bkifizLkmb1,
                       'data1': bkifizLkmb2,
                       'data2': bkifizLkmb3,
                       'data3': bkifizLkmb4,
                       'data4': bkifizLkmb5,
                       'data5': bkifizLkmb6,
                       'data6': bkifizLkmb7,
                       'data7': bkifizLkmb8,
                       'data8': bkifizLkmb9,
                       'data9': bkifizLkmb10,
                       'data10': bkifizLkmb11},
                success: function(response) {
                    // Предполагается, что сервер вернул ссылку на скачивание в переменной response.downloadLink
                    var downloadLink = response.downloadLink;

                    // Создаем скрытую ссылку для скачивания
                    var link = document.createElement('a');
                    var hrefValue, downloadValue;
                    log.console(bkifizLkmb2.length)
                    if (bkifizLkmb2.length > 110) {
                        hrefValue = '/static/temporary/БКИ _.docx';
                        downloadValue = 'БКИ _.docx';
                    } else {
                        hrefValue = '/static/temporary/БКИ ' + bkifizLkmb2 + '.docx';
                        downloadValue = 'БКИ ' + bkifizLkmb2 + '.docx';
                    }

                    // Присваиваем значение href в зависимости от условия
                    link.href = hrefValue;
                    link.download = downloadValue;  // Вставляем значение из bkiurLkmb2
                    document.body.appendChild(link);

                    // Имитируем клик по ссылке для начала скачивания
                    link.click();

                    // Удаляем временную ссылку
                    document.body.removeChild(link);
                }
            });
        });
    });

    <!--не дает странице обновиться при нажатии на кнопку "Скачать заявку по физ лицу ООО "ЛКМБ-РТ""-->
    document.getElementById("submit-button_fiz").addEventListener("click", function(event) {
            event.preventDefault();
        });
    <!--    делает неактивной кнопку "Скачать заявку по физ лицу ООО "ЛКМБ-РТ" при незаполненных данных. Срабатывает каждую секунду-->
        $(document).ready(function() {
        $('#submit-button_fiz').prop('disabled', true);

        setInterval(function() {
            if ($('#inputFiz1').val() !== '' && $('#inputFiz2').val() !== '' && $('#inputFiz3').val() !== ''
            && $('#inputFiz4').val() !== '' && $('#inputFiz5').val() !== '' && $('#inputFiz6').val() !== ''
            && $('#inputFiz7').val() !== '' && $('#inputFiz8').val() !== '' && $('#inputFiz9').val() !== ''
            && $('#inputFiz10').val() !== '' && $('#inputFiz11').val() !== '') {
                $('#submit-button_fiz').prop('disabled', false);
            } else {
                $('#submit-button_fiz').prop('disabled', true);
            }
        }, 1000);
    });