import json
import re

from bs4 import BeautifulSoup
from webapp.risk.download_page import read_delta_page
from webapp.risk.logger import logging


def info_delta(soup, title):
    try:
        title_element = soup.find('h2', string=title)
        if title_element:
            status_element = title_element.find_next('p', class_='more-card__table_text')
            if status_element:
                status_text = status_element.get_text(strip=True, separator=' ')
                return status_text
        else:
            return '-'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def defendant(soup):
    try:
        status_text = info_delta(soup, 'Арбитражные дела')
        if 'отсутствуют арбитражные' in status_text or 'Информация не найдена' in status_text:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def bankruptcy(soup, word):
    try:
        if word in soup.find('span', class_='grey', string='Статус:').nextSibling.lower().strip():
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info('Дельта рейтинг не 0')
        return 'Нет'


def bankruptcy_notices(soup):
    try:
        status_text = info_delta(soup, 'Сообщения о банкротстве')
        if 'отсутствуют сообщения' in status_text or 'Информация не найдена' in status_text:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def check_company_for_fssp(soup):
    target_pattern = r'.*не было возбуждено исполнительных производств.*'
    target_pattern2 = 'Информация не найдена'
    try:
        title_element = soup.find('h2', string='Исполнительные производства')
        if title_element:
            status_element = title_element.find_next('p', class_='more-card__table_text')
            if status_element:
                sentence = status_element.get_text(strip=True, separator=' ')
                match = re.search(r'(\d+)\s+руб(?:л[ей|я])', sentence)

                if re.search(target_pattern, sentence) or sentence == target_pattern2:
                    return 'Нет'

                if match:
                    number = int(match.group(1))
                    return 'Нет' if 100_000 > number else 'Да'

                return 'Да'
        else:
            return '-'

    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def mass_dir(soup):
    try:
        status_text = info_delta(soup, 'Массовость директоров/учредителей')
        if 'не является массовым' in status_text or 'Информация не найдена' in status_text:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def blocked_account(soup):
    try:
        status_text = info_delta(soup, 'Заблокированные расчетные счета')
        if 'по счетам налогоплательщика нет' in status_text:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def check_tax_debts(soup):
    target_pattern = r'Компания не имеет задолженностей по уплате основных налогов, превышающих 1000 рублей.*'
    target_pattern2 = r'.*На текущий момент у организации нет задолженности.'
    target_pattern3 = 'Информация не найдена'
    target_pattern4 = 'Не удалось получить информацию о превышении задолженности и предоставлении налоговой отчетности'
    try:
        status_text = info_delta(soup, 'Налоговая задолженность и отчетность')
        if re.search(target_pattern, status_text) or re.search(
                target_pattern2, status_text) or status_text == target_pattern3 or status_text == target_pattern4:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def gov_contracts(soup):
    try:
        status_text = info_delta(soup, 'Госконтракты')
        if 'не принимала' in status_text:
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def unscrupulous_seller(soup):
    try:
        status_text = info_delta(soup, 'Реестр недобросовестных поставщиков')
        if 'не числится' in status_text or 'не входит' in status_text:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def read_delta_html(client_inn, object_inn, short_name):
    try:
        soup = BeautifulSoup(read_delta_page(client_inn, object_inn, short_name), 'html.parser')
    except FileNotFoundError as _ex:
        logging.info(_ex, exc_info=True)
        raise _ex

    delta_description_of_the_company = {
        'Статус': info_delta(soup, 'Статус компании'),
        'Дата регистрации': info_delta(soup, 'Дата регистрации'),
        'Изменения в ЕГРЮЛ': info_delta(soup, 'Документы, поданные для регистрации/изменения в ЕГРЮЛ'),
        'Адрес регистрации': info_delta(soup, 'Адрес регистрации организации'),
        'Уставный капитал': info_delta(soup, 'Размер уставного капитала'),
        'Массовость директоров': info_delta(soup, 'Массовость директоров/учредителей'),
        'Дисквалифицированные лица': info_delta(soup, 'Дисквалифицированные лица'),
        'УФСКН': info_delta(soup, 'Преступления, связанные с оборотом наркотиков по данным УФСКН России'),
        'Смена директоров': info_delta(soup, 'Cмена директоров/учредителей'),
        'Госконтракты': info_delta(soup, 'Госконтракты'),
        'Сообщения о банкротстве': info_delta(soup, 'Сообщения о банкротстве'),
        'Налоговая задолженность': info_delta(soup, 'Налоговая задолженность и отчетность'),
        'Заблокированные расчетные счета': info_delta(soup, 'Заблокированные расчетные счета'),
        'Арбитражные дела': info_delta(soup, 'Арбитражные дела'),
        'Исполнительные производства': info_delta(soup, 'Исполнительные производства'),
        'Дочерние компания': info_delta(soup, 'Наличие дочерних компаний'),
        'Реестр недобросовестнных поставщиков': info_delta(soup, 'Реестр недобросовестных поставщиков'),
        'Процесс банкротства (да_нет)': bankruptcy(soup, 'банкрот'),  # for seller table
        'Процесс ликвидации (да_нет)': bankruptcy(soup, 'ликвид') and bankruptcy(soup, 'недейств'),  # for seller table
        'Процесс реорганизации (да_нет)': bankruptcy(soup, 'реорг'),  # for seller table
        'Ответчик (да_нет)': defendant(soup),  # for seller table
        'Сообщения о банкротстве (да_нет)': bankruptcy_notices(soup),  # for seller table
        'ФССП более 100 (да_нет)': check_company_for_fssp(soup),  # for seller table
        'Массовый руководитель (да_нет)': mass_dir(soup),  # for seller table
        'Налоговая задолженность (да_нет)': check_tax_debts(soup),  # for seller table
        'Заблокированные расчетные счета (да_нет)': blocked_account(soup),  # for seller table
        'Госконтракты (да_нет)': gov_contracts(soup),  # for seller table
        'Недобросовестный поставщик (да_нет)': unscrupulous_seller(soup),  # for seller table
    }

    with open(f'delta_info {object_inn}.json', 'a', encoding='utf-8') as file:
        json.dump(delta_description_of_the_company, file, ensure_ascii=False, indent=3)
        file.write('\n')
        file.write('\n')
        file.write('=' * 70)
        file.write('\n')
        file.write('\n')

    return delta_description_of_the_company
