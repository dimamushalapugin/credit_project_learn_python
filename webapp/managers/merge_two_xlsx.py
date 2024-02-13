# import win32com.client as win32
# import os
# import pythoncom
# from webapp.config import ABS_PATH_APP, ABS_PATH_TEMP


def merge_files(file_name, download_name):
    pass
    # # Получить полные пути к файлам
    # pythoncom.CoInitialize()
    # # Создать объекты приложений Excel
    # excel_app1 = win32.Dispatch("Excel.Application")
    # excel_app2 = win32.Dispatch("Excel.Application")
    #
    # file_path1 = os.path.join(ABS_PATH_TEMP, file_name)
    # file_path2 = os.path.join(ABS_PATH_APP, 'ШАБЛОН ЗАЯВКИ ЛКМБ.xlsx')
    # merged_file_path = os.path.join(ABS_PATH_TEMP, download_name)
    #
    # try:
    #     # Открыть первую и вторую книги Excel
    #     workbook1 = excel_app1.Workbooks.Open(file_path1)
    #     workbook2 = excel_app2.Workbooks.Open(file_path2)
    #
    #     # Копировать листы из первой книги во вторую
    #     for sheet_index in range(workbook1.Sheets.Count, 0, -1):
    #         sheet = workbook1.Sheets(sheet_index)
    #         sheet.Copy(Before=workbook2.Sheets(1))
    #
    #     # Сохранить изменения во второй книге
    #     workbook2.SaveAs(merged_file_path)
    #     workbook2.Close()
    #     workbook1.Close(SaveChanges=True)
    #
    # finally:
    #     # Закрыть книги и завершить работу с Excel
    #     excel_app1.Quit()
    #     excel_app2.Quit()
