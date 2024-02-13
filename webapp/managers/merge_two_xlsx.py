import os
import xlrd

from webapp.config import ABS_PATH_APP, ABS_PATH_TEMP
from xlutils.copy import copy as xl_copy


def merge_files(file_name, download_name):
    file_path1 = os.path.join(ABS_PATH_TEMP, file_name)
    file_path2 = os.path.join(ABS_PATH_APP, 'ШАБЛОН ЗАЯВКИ ЛКМБ.xlsx')
    merged_file_path = os.path.join(ABS_PATH_TEMP, download_name)

    try:
        # Открытие первого файла для чтения
        workbook1 = xlrd.open_workbook(file_path1, formatting_info=True)
        workbook2 = xlrd.open_workbook(file_path2, formatting_info=True)

        # Копирование листа из первого файла во второй
        wb1_sheet = workbook1.sheet_by_index(0)
        wb2 = xl_copy(workbook2)
        wb1 = wb2.add_sheet('Sheet1', cell_overwrite_ok=True)
        for row in range(wb1_sheet.nrows):
            for col in range(wb1_sheet.ncols):
                wb1.write(row, col, wb1_sheet.cell_value(row, col))

        # Сохранение изменений во втором файле
        wb2.save(merged_file_path)

    except Exception as e:
        print(f"Ошибка при объединении файлов: {e}")
