document.addEventListener('DOMContentLoaded', function () {
var loadingIndicator = document.getElementById('loading-indicator');
var submitButton = document.getElementById('submit-button');

submitButton.addEventListener('click', function () {
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

document.addEventListener('DOMContentLoaded', function () {
var loadingIndicator = document.getElementById('loading-indicator');
var submitButton = document.getElementById('submit-button1');

submitButton.addEventListener('click', function () {
    // Проверяем, заполнены ли обязательные поля
    var clientInn = document.getElementsByName('client_inn')[0].value;
    var sellerInn1 = document.getElementsByName('seller_inn1')[0].value;

    if (clientInn.trim() === '' || sellerInn1.trim() === '') {
        // Если хотя бы одно поле не заполнено, выходим из функции без дополнительных действий
        return;
    }

    // Показываем индикатор загрузки
    loadingIndicator.style.display = 'block';

    // Здесь можно добавить код для отправки формы или другие действия при нажатии на кнопку
    // Например, использовать AJAX для отправки данных на сервер и дождаться ответа

    setTimeout(function () {
    // Скрываем индикатор загрузки
        loadingIndicator.style.display = 'none';
    }, 20000); // 20000 миллисекунд = 20 секунд
            });
});