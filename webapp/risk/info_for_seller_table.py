import sys
import re

from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

from webapp.risk.logger import logging
from webapp.risk.parsing_html import date_of_registration  # по главной странице
from webapp.risk.download_page import read_main_page, read_delta_page

def bankruptcy(soup_delta, word):
    try:
        if word in soup_delta.find('span', class_='grey', string='Статус:').nextSibling.lower().strip():
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info('Дельта рейтинг не 0')
        return 'Нет'


def period_of_activity(soup_first):
    try:
        reg_comp_seller = dt.strptime(date_of_registration(soup_first), '%d.%m.%Y')
        cur_date_seller = dt.strptime(dt.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
        if relativedelta(cur_date_seller, reg_comp_seller).years >= 3:
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def inaccuracy_of_information(soup_delta):
    try:
        if 'недостоверн' in soup_delta.find(
                'div', class_='cards__column cards__column-first').get_text(' ', strip=True).lower():
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def defendant(soup_delta):
    try:
        title_element = soup_delta.find('h2', string='Арбитражные дела')
        if title_element:
            status_element = title_element.find_next('p', class_='more-card__table_text')
            if status_element:
                status_text = status_element.get_text(strip=True, separator=' ')
                if 'отсутствуют арбитражные' in status_text or 'Информация не найдена' in status_text:
                    return 'Нет'
                else:
                    return 'Да'
        else:
            return '-'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def bankruptcy_notices(soup_delta):
    try:
        title_element = soup_delta.find('h2', string='Сообщения о банкротстве')
        if title_element:
            status_element = title_element.find_next('p', class_='more-card__table_text')
            if status_element:
                status_text = status_element.get_text(strip=True, separator=' ')
                if 'отсутствуют сообщения' in status_text or 'Информация не найдена' in status_text:
                    return 'Да'
                else:
                    return 'Нет'
        else:
            return '-'
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def check_company_for_fssp(soup_delta):
    target_pattern = r'.*не было возбуждено исполнительных производств.*'
    target_pattern2 = 'Информация не найдена'
    try:
        title_element = soup_delta.find('h2', string='Исполнительные производства')
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


def read_pages(client_inn, object_inn, info_first, info_delta):
    print(info_first['Финансы'])
    print(info_first['Дата регистрации'])

    # info_table = {
    #     'Данные о контрагенте': 'Да',
    #     'Ликвидация': bankruptcy(soup_delta, 'ликвид') and bankruptcy(soup_delta, 'недейств'),
    #     'Банкротства': bankruptcy(soup_delta, 'банкрот'),
    #     'Реорганизация': bankruptcy(soup_delta, 'реорг'),
    #     'Недостоверности сведений': inaccuracy_of_information(soup_first),
    #     'Совпадение ИНН': 'Да',
    #     'Более 3 лет': period_of_activity(soup_first),
    #     'Ответчик': defendant(soup_delta),
    #     'Сообщения о банкротстве': bankruptcy_notices(soup_delta),
    #     'Исполнительные производства (более 100 тыс. руб.)': check_company_for_fssp(soup_delta),
    #     'Убыточность': '',
    #     'Адрес массовой регистрации': '',
    #     'Массовый руководитель': '',
    #     'Налоговая задолженность': '',
    #     'Заблокированные расч. сч.': '',
    #     'Экстремисткая деятельность': '',
    #     'Черный список ЦБ': '',
    #     'Гос. контракты': '',
    #     'Недобросовестные поставщики': '',
    #     'Завод-изготовитель': '',
    #     'Дилер/дистрибьютор': '',
    #     'История в ЛКМБ': ''
    # }
    #
    # for key, value in info_table.items():
    #     pprint(f'{key}: {value}')


# read_pages('1684000880', '0276974794')
# read_pages('1684000880', '7702087647')
# read_pages('1684000880', '2340017855')
