function validatePassportSeries(input) {
    // Заменяем все символы, кроме цифр, на пустую строку
    input.value = input.value.replace(/[^0-9]/g, '');
}