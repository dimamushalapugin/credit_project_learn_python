import json

from bs4 import BeautifulSoup
from pprint import pprint
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


def read_delta_html(client_inn, object_inn):
    try:
        soup = BeautifulSoup(read_delta_page(client_inn, object_inn), 'html.parser')
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
        'Реестр недобросовестнных поставщиков': info_delta(soup, 'Реестр недобросовестных поставщиков')
    }

    # for key, value in delta_description_of_the_company.items():
    #     pprint(f'{key}: {value}')

    return delta_description_of_the_company


# read_delta_html('1684000880', '0276974794')
# read_delta_html('1684000880', '1635010074')
