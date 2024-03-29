// Получаем ссылки на кнопки и инпуты для файлов
    var submitButton = document.getElementById("submit-button");
    var submitButton_individual = document.getElementById("submit-button-individual");
    var clientInnInput = document.getElementById('client_inn_form');
    var sellerInnInput = document.getElementById('seller_inn_form');
    var individualInn = document.getElementById('individual_inn');
    var individualName = document.getElementById('name');
    var individualSurname = document.getElementById('surname');
    var inputInn = document.getElementById('individual_inn');

    document.addEventListener('DOMContentLoaded', function () {
    var loadingIndicator = document.getElementById('loading-indicator');

    submitButton.addEventListener('click', function () {

        if (clientInnInput.value.trim() === '' || sellerInnInput.value.trim() === '') {
            return;
        }

        // Показываем индикатор загрузки
        loadingIndicator.style.display = 'block';
        // Здесь можно добавить код для отправки формы или другие действия при нажатии на кнопку
        // Например, использовать AJAX для отправки данных на сервер и дождаться ответа

        // В данном примере, просто устанавливаем событие, чтобы скрыть индикатор после полной загрузки страницы
        window.addEventListener('load', function () {
            // Скрываем индикатор загрузки
            loadingIndicator.style.display = 'none';
        });
    });
    submitButton_individual.addEventListener('click', function () {

        if (individualInn.value.trim() === '' || individualName.value.trim() === '' || individualSurname.value.trim() === '') {
            return;
        }

        // Показываем индикатор загрузки
        loadingIndicator.style.display = 'block';
        // Здесь можно добавить код для отправки формы или другие действия при нажатии на кнопку
        // Например, использовать AJAX для отправки данных на сервер и дождаться ответа
        // В данном примере, просто устанавливаем событие, чтобы скрыть индикатор после полной загрузки страницы
        window.addEventListener('load', function () {
            // Скрываем индикатор загрузки
            loadingIndicator.style.display = 'none';
        });
    });
});