import os
import xlwings as xw

from webapp.config import ABS_PATH_APP, ABS_PATH_TEMP


def merge_files(file_name, download_name):
    # Получить полные пути к файлам
    file_path1 = os.path.join(ABS_PATH_TEMP, file_name)
    file_path2 = os.path.join(ABS_PATH_APP, 'ШАБЛОН ЗАЯВКИ ЛКМБ.xlsx')
    merged_file_path = os.path.join(ABS_PATH_TEMP, download_name)

    # Открыть первую и вторую книги Excel
    workbook1 = xw.Book(file_path1)
    workbook2 = xw.Book(file_path2)

    # Копировать листы из первой книги во вторую
    for sheet in workbook1.sheets:
        sheet.api.Copy(Before=workbook2.sheets[0].api)

    # Сохранить изменения во второй книге
    workbook2.save(merged_file_path)
    workbook2.close()
    workbook1.close()

