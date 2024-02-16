var pathFile = "./upload_files";
// Получаем ссылки на кнопки и инпуты для файлов
var checkButton = document.getElementById("check-button");
var applicationFileInput = document.getElementById("applicationFileInput");
var graphicFileInput = document.getElementById("graphicFileInput");
var submitButton = document.getElementById("submit-button");
var plSelect = document.querySelector('select[name="pl"]');
var innSelect = document.querySelector('select[id="sellerInn"]');

applicationFileInput.addEventListener('change', function() {
    var file = applicationFileInput.files[0];

    if (file && file.name.endsWith('.xlsx')) {
        var reader = new FileReader();

        reader.onload = function(e) {
            var data = new Uint8Array(e.target.result);
            var workbook = XLSX.read(data, { type: 'array' });

            // Получаем значение из ячейки D6 первого листа
            var cellValue = workbook.Sheets[workbook.SheetNames[0]]['D6'].v;

            // Разделяем значение по символу "/" и берем только первую часть
            var firstPart = cellValue.split('/')[0];

            // Устанавливаем значение ИНН в соответствии с ячейкой D6
            document.getElementById('clientInn').value = firstPart;

            // Получаем значения из ячеек C21, C22, C23, C24 первого листа
            var plValues = [
                workbook.Sheets[workbook.SheetNames[0]]['C21'] ? workbook.Sheets[workbook.SheetNames[0]]['C21'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C22'] ? workbook.Sheets[workbook.SheetNames[0]]['C22'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C23'] ? workbook.Sheets[workbook.SheetNames[0]]['C23'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C24'] ? workbook.Sheets[workbook.SheetNames[0]]['C24'].v : '-'
            ];

            // Получаем значения из ячеек C11, C13, C15, C17 первого листа (ИНН ПРОДАВЦОВ)
            var innValues = [
                workbook.Sheets[workbook.SheetNames[0]]['C11'] ? workbook.Sheets[workbook.SheetNames[0]]['C11'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C13'] ? workbook.Sheets[workbook.SheetNames[0]]['C13'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C15'] ? workbook.Sheets[workbook.SheetNames[0]]['C15'].v : '-',
                workbook.Sheets[workbook.SheetNames[0]]['C17'] ? workbook.Sheets[workbook.SheetNames[0]]['C17'].v : '-'
            ];

            var sellerValues = [
                workbook.Sheets[workbook.SheetNames[0]]['A10'] ? workbook.Sheets[workbook.SheetNames[0]]['A10'].v : '',
                workbook.Sheets[workbook.SheetNames[0]]['A12'] ? workbook.Sheets[workbook.SheetNames[0]]['A12'].v : '',
                workbook.Sheets[workbook.SheetNames[0]]['A14'] ? workbook.Sheets[workbook.SheetNames[0]]['A14'].v : '',
                workbook.Sheets[workbook.SheetNames[0]]['A16'] ? workbook.Sheets[workbook.SheetNames[0]]['A16'].v : ''
            ];

            // Заполняем значения в <select>
            plSelect.options[1].text = plValues[0];
            plSelect.options[1].value = plValues[0];
            plSelect.options[2].text = plValues[1];
            plSelect.options[2].value = plValues[1];
            plSelect.options[3].text = plValues[2];
            plSelect.options[3].value = plValues[2];
            plSelect.options[4].text = plValues[3];
            plSelect.options[4].value = plValues[3];

            innSelect.options[1].text = sellerValues[0] + ', ' + innValues[0];
            innSelect.options[1].value = innValues[0];
            innSelect.options[2].text = sellerValues[1] + ', ' + innValues[1];
            innSelect.options[2].value = innValues[1];
            innSelect.options[3].text = sellerValues[2] + ', ' + innValues[2];
            innSelect.options[3].value = innValues[2];
            innSelect.options[4].text = sellerValues[3] + ', ' + innValues[3];
            innSelect.options[4].value = innValues[3];
        };

        reader.readAsArrayBuffer(file);
    }
})


function handleFileChange() {
var graphicFileInput = document.getElementById("graphicFileInput");
graphicFileInput.addEventListener('change', function() {
    var fileGraph = graphicFileInput.files[0];
    if ((fileGraph && fileGraph.name.endsWith('.xlsm')) || (fileGraph && fileGraph.name.endsWith('.xlsx'))) {
        var readerGraph = new FileReader();
        console.log("Change event triggered"); // Отладочный лог

        readerGraph.onload = function(e) {
            var dataGraph = new Uint8Array(e.target.result);
            var workbookGraph = XLSX.read(dataGraph, { type: 'array' });


            var graphSelect = document.getElementById("graphSelect");
            var sheetName = graphSelect.value; // Имя выбранного листа

            // Выводим сообщение о выбранном листе
            var selectedSheetMessage = "Выбран лист: " + sheetName;
            console.log(selectedSheetMessage);

            // Проверяем, что выбран нужный лист
            if (workbookGraph.SheetNames.includes(sheetName)) {
                // Получаем значение из ячейки B93 выбранного листа
                var cellValueGraph = workbookGraph.Sheets[sheetName]['B93']?.v;
                var checkButtonGraph = document.getElementById("check-button");
                console.log("Change event triggered"); // Отладочный лог3

                function handleClick() {
            if (cellValueGraph === undefined || cellValueGraph === "") {
                console.log("Condition is true");
                document.getElementById("message").innerHTML = "Уважаемый, в графике ячейка B93 пустая, просьба заполнить";

                // Show the message for 5 seconds
                setTimeout(function() {
                    document.getElementById("message").innerHTML = "";
                }, 5000);
            }
        }

                // Вызов функции обработчика события без нажатия на кнопку
                handleClick();
            }
        }

        readerGraph.readAsArrayBuffer(fileGraph);
    }
});
}

// Call the function проверка графика, ячейка B93
handleFileChange();
setInterval(checkFilesUploaded, 2000);

// Блокируем кнопку "Предпроверка" при загрузке страницы
checkButton.disabled = true;
submitButton.disabled = true;

// Функция для проверки загрузки обоих файлов и разблокировки кнопки "Предпроверка"
function checkFilesUploaded() {
    if (applicationFileInput.files.length > 0 && (!checkDl.checked || graphicFileInput.files.length > 0)) {
        // Если оба файла загружены или флажок не выбран, разблокируем кнопку "Предпроверка"
        checkButton.disabled = false;
    }
}
// Call the function проверка графика, ячейка B93
handleFileChange();

// Добавляем обработчик события change для обоих инпутов файлов
applicationFileInput.addEventListener("change", checkFilesUploaded);
graphicFileInput.addEventListener("change", checkFilesUploaded);

// Обработчик события для кнопки "Предпроверка"
checkButton.addEventListener("click", function() {
    // Создаем объект FormData для загрузки файлов
    var formData = new FormData();
    formData.append('uploaded_application', applicationFileInput.files[0]);
    formData.append('uploaded_graphic', graphicFileInput.files[0]);

    // Отправляем файлы на сервер
    fetch(pathFile, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data); // Обработка данных с сервера после загрузки файлов

        // После успешной загрузки и сохранения файлов, можно выполнить дополнительные действия
        checkButton.disabled = true;
        submitButton.disabled = false;
    });
});