import os
import time
from pprint import pprint

from dadata import Dadata
from datetime import datetime as dt

from flask_login import current_user

from webapp.config import PATH_FOR_HTML_PAGES, DADATA_TOKEN, URL_DELTA, PATH_FOR_HTML_PAGES_IND
from webapp.risk.search_client import search_client, update_page
from webapp.risk.logger import logging
from webapp.risk.download_page import download_main_page, download_delta_page
from webapp.risk.parsing_html import read_main_html, read_main_html_individual
from webapp.risk.parsing_delta_html import read_delta_html
from webapp.risk.info_for_seller_table import read_pages_for_table, read_pages_for_table_individual
from webapp.risk.create_xlsx import create_xlsx_file, create_xlsx_file_individual


def create_conclusion(client_inn, seller_inn, is_factory, is_dealer):
    logging.info("=" * 50)
    logging.info(f"START ({current_user})")
    logging.info("=" * 50)

    try:
        result_about_company = Dadata(DADATA_TOKEN).find_by_id("party", client_inn)
        short_name = result_about_company[0]['data']['name']['short_with_opf'].replace('"', '')
    except Exception:
        short_name = ''

    logging.info('Создаем папку под данный проект')
    try:
        if not os.path.exists(
                fr'{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f"%d.%m.%Y")}'):
            os.makedirs(fr'{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f"%d.%m.%Y")}')
    except Exception as ex:
        logging.info(ex, exc_info=True)
        if 'КФУ' in short_name:
            short_name = 'КФУ'
        else:
            short_name = '-'
        if not os.path.exists(
                fr'{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f"%d.%m.%Y")}'):
            os.makedirs(fr'{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f"%d.%m.%Y")}')

    driver = search_client(client_inn, caller='create_conclusion')

    logging.info('Обновляем страницу лизингополучателя')
    update_page(client_inn, driver)

    logging.info('Скачиваем страницу компании лизингополучателя')
    download_main_page(driver, client_inn, client_inn, short_name)  # driver, папка ЛП, объект

    logging.info('Открываем главную страницу компании лизингополучателя на чтение')
    if len(client_inn) == 10:
        all_information_from_main_page = read_main_html(client_inn, client_inn, short_name)
    else:
        all_information_from_main_page = read_main_html_individual(client_inn, client_inn, short_name)

    time.sleep(15)

    match len(client_inn):
        case 10:
            logging.info('Запуск процесса загрузки страницы Дельта Аналитики')
            download_delta_page(driver, all_information_from_main_page, client_inn,
                                client_inn, short_name)  # driver, data, папка ЛП, объект

            logging.info('Запуск процесса чтения страницы Дельта Аналитики')
            all_information_from_delta_page = read_delta_html(client_inn, client_inn, short_name)  # ЛП, объект

        case _:
            all_information_from_delta_page = None
            logging.info('Отсутствует страница Дельта Аналитики')

    logging.info('Запуск процесса проверки директора')
    if len(client_inn) == 10:
        driver.execute_script(f"window.open('{URL_DELTA}"
                              f"{all_information_from_main_page['ССЫЛКА НА ДИРЕКТОРА']}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        director_inn = all_information_from_main_page['ЕГРЮЛ/ИНН ДИРЕКТОРА'].split()[-1]
        logging.info('Обновляем страницу директора')
        update_page(director_inn, driver)
        logging.info('Скачиваем страницу директора')
        download_main_page(driver, client_inn, director_inn, short_name)
        all_information_about_director = read_main_html_individual(client_inn, director_inn, short_name)
        driver.implicitly_wait(3)
        driver.close()
        logging.info(f"Возвращаемся обратно на главную страницу компании")
        driver.switch_to.window(driver.window_handles[1])
        logging.info(f"Current URL: {driver.current_url}")

    else:
        logging.info('Проверка директора не нужна (Лизингополучатель ИП/КФХ)')
        all_information_about_director = None

    logging.info('Запуск процесса проверки учредителей ФЛ')
    all_information_about_founders = {}
    if len(client_inn) == 10:
        for founder in all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'].keys():
            if all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['href']:
                if all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['director'] is False:
                    driver.execute_script(
                        f"window.open('{URL_DELTA}"
                        f"{all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['href']}', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                    founder_inn = all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['inn'].split()[1]
                    logging.info('Обновляем страницу учредителя')
                    update_page(founder_inn, driver)
                    logging.info('Скачиваем страницу учредителя')
                    download_main_page(driver, client_inn, founder_inn, short_name)
                    dict_founders = read_main_html_individual(client_inn, founder_inn, short_name)
                    driver.implicitly_wait(3)
                    driver.close()
                    logging.info(f"Возвращаемся обратно на главную страницу компании")
                    driver.switch_to.window(driver.window_handles[1])
                    logging.info(f"Current URL: {driver.current_url}")
                    all_information_about_founders.setdefault(founder, dict_founders)
                    all_information_about_founders[founder].setdefault('full_name',
                                                                       all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][
                                                                           founder]['full_name'])
                    all_information_about_founders[founder].setdefault('percent',
                                                                       all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][
                                                                           founder]['percent'])
                else:
                    logging.info('УЧРЕДИТЕЛЬ = ДИРЕКТОР')
                    all_information_about_founders.setdefault(founder, {
                        'full_name': all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['full_name'],
                        'percent': all_information_from_main_page['УЧРЕДИТЕЛИ ФЛ'][founder]['percent']})
            else:
                logging.info('Проверерь учредителя невозможно. Возможно информация скрыта.')
    else:
        logging.info('Проверка учредителей не нужна (Лизингополучатель ИП/КФХ)')
        all_information_about_founders = None

    driver.quit()

    all_information_from_main_page_seller = None
    all_information_from_delta_page_seller = None
    if seller_inn != client_inn:
        logging.info('Запуск процесса получения данных по продавцу')

        driver = search_client(seller_inn, caller='create_conclusion')

        logging.info('Обновляем страницу продавца')
        update_page(seller_inn, driver)

        logging.info('Скачиваем страницу продавца')
        download_main_page(driver, client_inn, seller_inn, short_name)  # driver, папка ЛП, объект

        logging.info('Открываем главную страницу продавца на чтение')
        if len(seller_inn) == 10:
            all_information_from_main_page_seller = read_main_html(client_inn, seller_inn, short_name)
        else:
            all_information_from_main_page_seller = read_main_html_individual(client_inn, seller_inn, short_name)

        time.sleep(15)

        match len(seller_inn):
            case 10:
                logging.info('Запуск процесса загрузки страницы продавца Дельта Аналитики')
                download_delta_page(driver, all_information_from_main_page_seller, client_inn,
                                    seller_inn, short_name)  # driver, data, папка ЛП, объект

                logging.info('Запуск процесса чтения страницы продавца Дельта Аналитики')
                all_information_from_delta_page_seller = read_delta_html(client_inn, seller_inn,
                                                                         short_name)  # ЛП, объект

            case _:
                all_information_from_delta_page_seller = None
                logging.info('Отсутствует страница продавца Дельта Аналитики')

        if len(seller_inn) == 10:
            seller_check_list = read_pages_for_table(seller_inn, all_information_from_main_page_seller,
                                                     all_information_from_delta_page_seller, is_factory, is_dealer)
        else:
            seller_check_list = read_pages_for_table_individual(seller_inn, all_information_from_main_page_seller,
                                                                is_factory, is_dealer)
    else:
        seller_check_list = None
        logging.info('Возвратный лизинг. Проверка клиента уже проведена.')

    logging.info('Запуск процесса формирования xlsx файла')
    create_xlsx_file(client_inn, seller_inn, all_information_from_main_page, all_information_from_delta_page,
                     all_information_about_director,
                     all_information_about_founders, all_information_from_main_page_seller,
                     all_information_from_delta_page_seller, seller_check_list, short_name)

    driver.quit()

    logging.info(f'END! ({current_user})')


class IndividualParams:
    def __init__(self, dict_params):
        self._data = {form_name: value.strip() if isinstance(value, str) else value for form_name, value in
                      dict_params.items()}

    @property
    def get_name(self):
        return self._data['name']

    @property
    def get_surname(self):
        return self._data['surname']

    @property
    def get_patronymic(self):
        return self._data['patronymic']

    @property
    def get_full_name(self):
        return f'{self._data["surname"]} {self._data["name"]} {self._data["patronymic"]}'

    @property
    def get_inn(self):
        return self._data['individual_inn']

    @property
    def get_passport_series(self):
        return self._data['series_passport']

    @property
    def get_passport_number(self):
        return self._data['number_passport']

    @property
    def get_date_of_birth(self):
        input_date = self._data['date_birth']
        try:
            formatted_date = dt.strptime(input_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError:
            formatted_date = ''
        return formatted_date


def create_conclusion_individual(params):
    logging.info(f'{current_user} - Нажал на кнопку "Проверка физ. лица"')
    logging.info("=" * 50)
    logging.info(f"START ({current_user})")
    logging.info("=" * 50)

    person = IndividualParams(params)
    logging.info('Создаем папку под данный проект')
    try:
        if not os.path.exists(
                fr'{PATH_FOR_HTML_PAGES_IND}/{person.get_full_name} ИНН {person.get_inn}/{dt.today().strftime(f"%d.%m.%Y")}'):
            os.makedirs(
                fr'{PATH_FOR_HTML_PAGES_IND}/{person.get_full_name} ИНН {person.get_inn}/{dt.today().strftime(f"%d.%m.%Y")}')
    except Exception as ex:
        logging.info(ex, exc_info=True)
        raise ex

    driver = search_client(person.get_inn)
    logging.info('Обновляем страницу лизингополучателя')
    update_page(person, driver, person=person)
    logging.info('Скачиваем страницу физ. лица')
    download_main_page(driver, person.get_inn, person.get_inn, person.get_full_name, True)
    all_information_about_individual = read_main_html_individual(person.get_inn, person.get_inn, person.get_full_name,
                                                                 True)
    driver.implicitly_wait(3)
    driver.close()
    driver.quit()
    logging.info('Запуск процесса формирования xlsx файла')
    create_xlsx_file_individual(all_information_about_individual, person)
