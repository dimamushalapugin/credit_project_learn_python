import win32com.client as win32
from webapp.config import APPLICATION_PATH_LKMB


def merge_files(app_path):
    # Получить полные пути к файлам

    # Создать объекты приложений Excel
    excel_app1 = win32.Dispatch("Excel.Application")
    excel_app2 = win32.Dispatch("Excel.Application")

    try:
        # Открыть первую и вторую книги Excel
        workbook1 = excel_app1.Workbooks.Open(APPLICATION_PATH_LKMB)
        workbook2 = excel_app2.Workbooks.Open(app_path)

        # Копировать листы из второй книги в первую
        for sheet_index in range(workbook1.Sheets.Count, 0, -1):
            sheet = workbook1.Sheets(sheet_index)
            sheet.Copy(Before=workbook2.Sheets(1))

        # Сохранить изменения в первой книге
        workbook2.SaveAs(app_path)

    finally:
        # Закрыть книги и завершить работу с Excel
        workbook1.Close()
        workbook2.Close()
        excel_app1.Quit()
        excel_app2.Quit()
