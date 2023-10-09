import openpyxl

from datetime import datetime as dt

from webapp.risk.logger import logging
from webapp.config import PATH_FOR_HTML_PAGES


def create_xlsx_file(inn_client, inn_seller, main_client: dict, delta_client: dict, director_client: dict,
                     founders_client: dict, main_seller: dict,
                     delta_seller: dict, last_table_seller: dict, short_name: str):
    """main_client: can't be None
       delta_client: can be None, если клиент ИП/КФХ/физик
       director_client: can be None, если клиент ИП/КФХ/физик
       founders_client: can be None, если клиент ИП/КФХ/физик
       main_seller: can be None, если Возвратный
       delta_seller: can be None, если Возвратный/если клиент ИП/КФХ/физик
       last_table_seller: can be None, если Возвратный"""

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet['A1'].value = f'Риск заключение по {main_client["Краткое наименование"]} на {dt.today().strftime(f"%d.%m.%Y")}'

    sheet[f'A{sheet.max_row + 1}'].value = '1. Общее описание Лизингополучателя'

    """Если клиент Юр. лицо, то попадаем в if"""
    if len(inn_client) == 10:
        logging.info('Клиент юр. лицо. Идет заполнение файла...')
        sheet[f'A{sheet.max_row + 1}'].value = 'Наименование поля'
        sheet[f'B{sheet.max_row}'].value = 'Значение'

        for index, (name, value) in enumerate(main_client.items()):
            if index == 22:  # Кол-во итераций. Заканчивается на "ИСТОРИЯ"
                break
            match value:
                case str():
                    logging.info(f"{index} {name}: {value} (string)")
                    sheet[f'A{sheet.max_row + 1}'].value = name
                    sheet[f'B{sheet.max_row}'].value = value
                case dict():
                    logging.info(f"{index} {name}: {value} (dict)")
                    some_list = []
                    try:
                        logging.info(main_client.get(name))
                        for num in main_client.get(name):
                            some_list.append(f'{num}) {main_client.get(name).get(num).get("percent")} {main_client.get(name).get(num).get("sum")} {main_client.get(name).get(num).get("full_name")} {main_client.get(name).get(num).get("inn")} {main_client.get(name).get(num).get("egrul")}')
                    except TypeError:
                        logging.info("Попал в except")
                    sheet[f'A{sheet.max_row + 1}'].value = name
                    if len(some_list) > 0:
                        sheet[f'B{sheet.max_row}'].value = "\n".join(some_list)
                    else:
                        sheet[f'B{sheet.max_row}'].value = '-'
                case _:
                    logging.info(f"{index} {name}: {value} (other)")
                    sheet[f'A{sheet.max_row + 1}'].value = name
                    sheet[f'B{sheet.max_row}'].value = '-'

    logging.info("Сохраняем файл")
    wb.save(fr"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {inn_client}/{dt.today().strftime(f'%d.%m.%Y')}/Риск заключение {inn_client}.xlsx")

