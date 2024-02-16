// Получаем ссылки на чекбоксы и дополнительные поля
const checkDl = document.getElementById("check_dl");
const checkDkp = document.getElementById("check_dkp");
const dlFields = document.getElementById("dl_fields");
const dkpFields = document.getElementById("dkp_fields");
const mainFields = document.getElementById("main_fields");
const typeSelect = document.getElementById("typeSelect");
const dopFields = document.getElementById("dop_fields");
const stockEx = document.getElementById("stock");
const currency = document.getElementById("currency");
const stockSelect = document.querySelector('[name="stock"]');
const graphSelect = document.getElementById("graphSelect");

graphSelect.addEventListener("change", function() {
const selectedValue = graphSelect.value;
const divField = document.getElementById("divField");

if (selectedValue) {
    divField.style.display = "block";
} else {
    divField.style.display = "none";
}
});

// Добавляем слушатели событий на чекбоксы
checkDl.addEventListener("change", function() {
    if (checkDl.checked) {
        dlFields.style.display = "block";
        enableFields(dlFields);
        updateCheckButtonDl();
        updateMainAndAppFields();
    } else {
        dlFields.style.display = "none";
        disableFields(dlFields);
        updateCheckButtonDl();
        updateMainAndAppFields();
    }
});

checkDkp.addEventListener("change", function() {
    if (checkDkp.checked) {
        dkpFields.style.display = "block";
        enableFields(dkpFields);
        updateDopFields();
        updateCheckButtonDkp();
        updateMainAndAppFields();
        updateStock();
    } else {
        dkpFields.style.display = "none";
        disableFields(dkpFields);
        updateDopFields();
        updateCheckButtonDkp();
        updateMainAndAppFields();
        updateStock();
    }
});

// Добавляем слушатель события изменения выбора
typeSelect.addEventListener("change", function() {
    if (typeSelect.checked && checkDkp.checked) {
        dopFields.style.display = "block";
        enableFields(dopFields);
        updateDopFields();
    } else {
        dopFields.style.display = "none";
        disableFields(dopFields);
        updateDopFields();
    }
});

// Добавляем слушатель события для поля ЦБ или Биржа
currency.addEventListener("change", function () {
    updateStock();
});

function updateMainAndAppFields() {
    if (checkDl.checked || checkDkp.checked) {
        mainFields.style.display = "block";
        enableFields(mainFields);
    } else {
        mainFields.style.display = "none";
        disableFields(mainFields);
    }
}

function updateDopFields() {
    if (typeSelect.checked && checkDkp.checked) {
        dopFields.style.display = "block";
        enableFields(dopFields);
    } else {
        dopFields.style.display = "none";
        disableFields(dopFields);
    }
}
function updateStock() {
    if ((currency.value === "Китайский юань" || currency.value === "Доллар США" || currency.value === "Евро") && checkDkp.checked) {
        stockEx.style.display = "block";
        enableFields(stockEx)
    } else {
        stockEx.style.display = "none";
        // Отключаем возможность выбора опций в блоке "stock"
        disableFields(stockEx);
    }
}

function updateCheckButtonDl() {
    if (checkDl.checked && (applicationFileInput.files.length > 0 && graphicFileInput.files.length > 0)) {
        checkButton.disabled = false;
    } else {
        checkButton.disabled = true;
    }
}

function updateCheckButtonDkp() {
    if (checkDkp.checked && (applicationFileInput.files.length > 0)) {
        checkButton.disabled = false;
    } else {
        checkButton.disabled = true;
    }
}

// Функция для отключения элементов и добавления атрибута disabled
function disableFields(container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach(input => {
        input.disabled = true;
    });
}

// Функция для включения элементов и удаления атрибута disabled
function enableFields(container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach(input => {
        input.disabled = false;
    });
}