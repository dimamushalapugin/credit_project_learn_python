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
    sheet[
        'A1'].value = f'Риск заключение по {main_client["Краткое наименование"]} на {dt.today().strftime(f"%d.%m.%Y")}'

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
                            some_list.append(
                                f'{num}) {main_client.get(name).get(num).get("percent")} {main_client.get(name).get(num).get("sum")} {main_client.get(name).get(num).get("full_name")} {main_client.get(name).get(num).get("inn")} {main_client.get(name).get(num).get("egrul")}')
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

        sheet[f'A{sheet.max_row + 2}'].value = '2. Анализ деятельности'
        sheet[f'A{sheet.max_row + 1}'].value = delta_client['Рейтинг дельта номер']
        sheet[f'B{sheet.max_row}'].value = delta_client['Рейтинг дельта текст']
        sheet[f'A{sheet.max_row + 1}'].value = 'Рейтинг'
        sheet[f'B{sheet.max_row}'].value = 'Описание'
        delta_rating_dict = {'100': 'Благонадежность  предприятия очень высокая.',
                             '90': 'Вероятность благонадежности предприятия высокая.',
                             '80': 'У предприятия имеется один или несколько признаков неблагонадежности.',
                             '70': 'У предприятия имеется несколько признаков неблагонадежности',
                             '50-60': 'Взаимодействие с данной фирмой может быть сопряжено со средней степенью риска.',
                             '40': 'Взаимодействие с данной фирмой может быть сопряжено с высокой степенью риска.',
                             '0-30': 'Сотрудничество с данной компанией нежелательно'}

        for key, value in delta_rating_dict.items():
            sheet[f'A{sheet.max_row + 1}'].value = key
            sheet[f'B{sheet.max_row}'].value = value

        sheet[f'A{sheet.max_row + 2}'].value = 'Анализ регистрационных данных'
        for index, (key, value) in enumerate(delta_client.items()):
            if index == 5:
                break
            sheet[f'A{sheet.max_row + 1}'].value = key
            sheet[f'B{sheet.max_row}'].value = value

        sheet[f'A{sheet.max_row + 2}'].value = 'Анализ директоров/учредителей'
        for index, (key, value) in enumerate(delta_client.items()):
            if index == 9:
                break
            if index >= 5:
                sheet[f'A{sheet.max_row + 1}'].value = key
                sheet[f'B{sheet.max_row}'].value = value

        sheet[f'A{sheet.max_row + 2}'].value = 'Анализ деятельности'
        for index, (key, value) in enumerate(delta_client.items()):
            if index == 17:
                break
            if index >= 9:
                sheet[f'A{sheet.max_row + 1}'].value = key
                sheet[f'B{sheet.max_row}'].value = value

        sheet[f'A{sheet.max_row + 2}'].value = 'ФИНАНСОВЫЕ ПОКАЗАТЕЛИ'
        columns_list = ['B', 'C', 'D']
        columns_list_index = 0
        num_for_values = -5

        try:
            if main_client['Финансы'].get(2022):
                sheet[f'A{sheet.max_row + 1}'].value = 'НАИМЕНОВАНИЕ'
                sheet[f'A{sheet.max_row + 1}'].value = 'Баланс'
                sheet[f'A{sheet.max_row + 1}'].value = 'Выручка'
                sheet[f'A{sheet.max_row + 1}'].value = 'Обязательства'
                sheet[f'A{sheet.max_row + 1}'].value = 'Чистая прибыль'
                sheet[f'A{sheet.max_row + 1}'].value = 'Капитал и резервы'
                sheet[f'A{sheet.max_row + 1}'].value = 'Основные средства'
                for key in main_client['Финансы']:
                    sheet[f'{columns_list[columns_list_index]}{sheet.max_row - 6}'].value = key
                    for indicators, values in main_client['Финансы'][key].items():
                        sheet[f'{columns_list[columns_list_index]}{sheet.max_row + num_for_values}'].value = values
                        num_for_values += 1
                    num_for_values = -5
                    columns_list_index += 1
            else:
                sheet[f'A{sheet.max_row + 1}'].value = 'Отсутствуют финансовые показатели'
        except Exception:
            sheet[f'A{sheet.max_row + 1}'].value = '-'

        sheet[f'A{sheet.max_row + 2}'].value = 'НАЛОГИ И СБОРЫ'
        sheet[f'B{sheet.max_row}'].value = main_client['Налоги и сборы']

        sheet[f'A{sheet.max_row + 2}'].value = 'АФФИЛИРОВАННЫЕ И СВЯЗАННЫЕ ЛИЦА'
        sheet[f'A{sheet.max_row + 1}'].value = ''

        sheet[f'A{sheet.max_row + 2}'].value = 'СУЩЕСТВЕННЫЕ ФАКТЫ ПО ДАННЫМ ФЕДРЕСУРСА'
        sheet[f'A{sheet.max_row + 1}'].value = main_client['Федресурс']

        sheet[f'A{sheet.max_row + 2}'].value = 'СВЕДЕНИЯ ИЗ РЕЕСТРА ЗАЛОГОВ'
        sheet[f'A{sheet.max_row + 1}'].value = main_client['Реестр залогов']

        sheet[f'A{sheet.max_row + 2}'].value = 'РОСФИНМОНИТОРИНГ(ТЕРРОРИСТИЧЕСКИЕ ОРГАНИЗАЦИИ)'
        sheet[f'A{sheet.max_row + 1}'].value = main_client['Росфинмониторинг']

        sheet[f'A{sheet.max_row + 2}'].value = 'САНКЦИИ США, ЕС, КАНАДЫ (ЮЛ)'
        sheet[f'A{sheet.max_row + 1}'].value = main_client['Санкции']

        sheet[f'A{sheet.max_row + 2}'].value = 'ЧЕРНЫЙ СПИСОК ЦБ РФ (ЮЛ)'
        sheet[f'A{sheet.max_row + 1}'].value = main_client['Черный список']

        logging.info("Запуск процесса записи информации про директора/учредителей в xslx файл")
        sheet[f'A{sheet.max_row + 2}'].value = '3. Анализ директора/учредителей'
        sheet[f'A{sheet.max_row + 1}'].value = '3.1. ДИРЕКТОР/ГЕН. ДИРЕКТОР'
        sheet[f'A{sheet.max_row + 1}'].value = director_client['Краткое наименование']
        sheet[f'A{sheet.max_row + 1}'].value = ''

        def write_user(data):
            for index, (key, value) in enumerate(data.items()):
                if index == 4:  # Кол-во итераций
                    break
                sheet[f'A{sheet.max_row + 1}'].value = key
                sheet[f'B{sheet.max_row}'].value = value

            sheet[f'A{sheet.max_row + 2}'].value = 'Регистрация в качестве индивидуального предпринимателя:'
            if data['Инфо_ИП']:
                for num in data['Инфо_ИП']:
                    for key, value in data['Инфо_ИП'][num].items():
                        sheet[f'A{sheet.max_row + 1}'].value = key
                        sheet[f'B{sheet.max_row}'].value = value
                    sheet[f'A{sheet.max_row + 1}'].value = ''
            else:
                sheet[f'A{sheet.max_row + 1}'].value = 'Информация отсутствует'
                sheet[f'A{sheet.max_row + 1}'].value = ''

            sheet[f'A{sheet.max_row + 1}'].value = 'Адрес регистрации:'
            sheet[f'B{sheet.max_row}'].value = data['Адрес_регистрации']

            sheet[f'A{sheet.max_row + 2}'].value = 'Информация о регистрирующем органе:'
            sheet[f'B{sheet.max_row}'].value = data['Имя_налог_органа']

            sheet[f'A{sheet.max_row + 2}'].value = 'Является руководителем:'
            sheet[f'B{sheet.max_row}'].value = 'Является учредителем:'
            sheet[f'A{sheet.max_row + 1}'].value = data['История_руководства']['Является руководителем']
            sheet[f'B{sheet.max_row}'].value = data['История_руководства']['Является учредителем']
            sheet[f'A{sheet.max_row + 1}'].value = 'Являлся руководителем:'
            sheet[f'B{sheet.max_row}'].value = 'Являлся учредителем:'
            sheet[f'A{sheet.max_row + 1}'].value = data['История_руководства']['Являлся руководителем']
            sheet[f'B{sheet.max_row}'].value = data['История_руководства']['Являлся учредителем']

            for index, (key, value) in enumerate(data.items()):
                if index == 24:  # Кол-во итераций
                    break
                if index >= 9:
                    sheet[f'A{sheet.max_row + 2}'].value = key
                    sheet[f'A{sheet.max_row + 1}'].value = value

        write_user(director_client)

        sheet[f'A{sheet.max_row + 2}'].value = '3.2. УЧРЕДИТЕЛИ:'
        sheet[f'A{sheet.max_row + 1}'].value = 'Учредители ЮЛ'

        founders_list_ul = []
        name_ul = "УЧРЕДИТЕЛИ ЮЛ"
        try:
            for num in main_client.get(name_ul):
                founders_list_ul.append(
                    f'{num}) {main_client.get(name_ul).get(num).get("percent")} {main_client.get(name_ul).get(num).get("sum")} {main_client.get(name_ul).get(num).get("full_name")} {main_client.get(name_ul).get(num).get("inn")} {main_client.get(name_ul).get(num).get("egrul")}')
        except TypeError as _ex:
            logging.info("Попал в except")
            logging.info(_ex, exc_info=True)
        if len(founders_list_ul) > 0:
            sheet[f'B{sheet.max_row}'].value = "\n".join(founders_list_ul)
        else:
            sheet[f'B{sheet.max_row}'].value = '-'

        sheet[f'A{sheet.max_row + 2}'].value = 'Учредители ФЛ'

        founders_list_fl = []
        name_fl = "УЧРЕДИТЕЛИ ФЛ"
        try:
            for num in main_client.get(name_fl):
                founders_list_fl.append(
                    f'{num}) {main_client.get(name_fl).get(num).get("percent")} {main_client.get(name_fl).get(num).get("sum")} {main_client.get(name_fl).get(num).get("full_name")} {main_client.get(name_fl).get(num).get("inn")} {main_client.get(name_fl).get(num).get("egrul")}')
        except TypeError as _ex:
            logging.info("Попал в except")
            logging.info(_ex, exc_info=True)
        if len(founders_list_fl) > 0:
            sheet[f'B{sheet.max_row}'].value = "\n".join(founders_list_fl)
        else:
            sheet[f'B{sheet.max_row}'].value = '-'

        try:
            if main_client['УЧРЕДИТЕЛИ ФЛ']:
                for num in founders_client:
                    if len(founders_client[num]) > 2:
                        sheet[f'A{sheet.max_row + 2}'].value = f'УЧРЕДИТЕЛЬ {num} {founders_client[num]["percent"]}'
                        sheet[f'A{sheet.max_row + 1}'].value = founders_client[num]["full_name"]
                        sheet[f'A{sheet.max_row + 1}'].value = ''
                        write_user(founders_client[num])
                        sheet[f'A{sheet.max_row + 1}'].value = ''
                    else:
                        sheet[
                            f'A{sheet.max_row + 2}'].value = f'УЧРЕДИТЕЛЬ {num} {founders_client[num]["percent"]} (ДИРЕКТОР)'
                        sheet[f'A{sheet.max_row + 1}'].value = founders_client[num]["full_name"]
                        sheet[f'A{sheet.max_row + 1}'].value = 'Проверка директора уже проведена'
                        sheet[f'A{sheet.max_row + 1}'].value = ''

        except Exception as _ex:
            logging.info(_ex, exc_info=True)

    logging.info("Сохраняем файл")
    wb.save(
        fr"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {inn_client}/{dt.today().strftime(f'%d.%m.%Y')}/Риск заключение {inn_client}.xlsx")
