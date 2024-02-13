import os
import xlwings as xw

from webapp.config import ABS_PATH_APP, ABS_PATH_TEMP


def merge_files(file_name, download_name):
    file_path1 = os.path.join(ABS_PATH_TEMP, file_name)
    file_path2 = os.path.join(ABS_PATH_APP, 'ШАБЛОН ЗАЯВКИ ЛКМБ.xlsx')
    merged_file_path = os.path.join(ABS_PATH_TEMP, download_name)

    # Подключение к серверу xlwings
    app = xw.App(visible=False)

    try:
        # Открытие книг Excel
        workbook1 = app.books.open(file_path1)
        workbook2 = app.books.open(file_path2)

        # Копирование листов
        for sheet in workbook1.sheets:
            sheet.api.Copy(Before=workbook2.sheets[0].api)

        # Сохранение и закрытие
        workbook2.save(merged_file_path)
        workbook2.close()
        workbook1.close()

    finally:
        # Закрытие приложения
        app.quit()
