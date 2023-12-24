import openpyxl
import os

from datetime import datetime as dt
from typing import Optional
from docx import Document
from num2words import num2words
from flask_login import current_user
from webapp.config import DADATA_BASE
from webapp.risk.logger import logging
from webapp.risk.mongo_db import MongoDB


def start_filling_application(inn_leasee, path_application, inn_seller1, inn_seller2, inn_seller3, inn_seller4):
    mongo = MongoDB(current_user)
    logging.info(f"({current_user}) Этап 1.")
    temporary_path = r'webapp\static\temporary'
    path_for_download = r'static\temporary'
    ip_or_kfh = 'Нет'
    type_business = ''
    full_krakt_name_leasee = ''
    main_activity_leasee = ''
    ogrn_leasee = ''
    okpo_leasee = ''
    okato_leasee = ''
    date_regist = ''
    ustav_capital = ''
    inn_kpp_leasee = ''
    address_leasee = ''
    formatted_name_leader_leasee = ''
    fio_list = ''
    inn_list = ''
    dolya_list = ''
    full_name_leasee = ''
    leader_leasee = ''
    fio_leader = ''
    phone_leasee = ''
    email_leasee = ''
    krakt_name_seller1 = ''
    krakt_name_seller2 = ''
    krakt_name_seller3 = ''
    krakt_name_seller4 = ''
    address_seller1 = ''
    address_seller2 = ''
    address_seller3 = ''
    address_seller4 = ''
    inn_dir_leasee = ''

    def parser_info_leasee(inn_leasee):
        logging.info(f"({current_user}) Этап 2.")
        nonlocal ip_or_kfh, type_business, inn_dir_leasee, krakt_name_seller1, address_seller1, krakt_name_seller2, address_seller2, krakt_name_seller3, address_seller3, krakt_name_seller4, address_seller4, full_krakt_name_leasee, main_activity_leasee, ogrn_leasee, okpo_leasee, okato_leasee, date_regist, ustav_capital, inn_kpp_leasee, address_leasee, formatted_name_leader_leasee, fio_list, inn_list, dolya_list, full_name_leasee, leader_leasee, fio_leader, phone_leasee, email_leasee

        logging.info(f"({inn_leasee})")

        dadata = Dadata(DADATA_TOKEN)
        result = dadata.find_by_id("party", inn_leasee)
        # logging.info(f"{result}")

        ip_or_kfh = 'Нет'
        if result[0]['data']['opf']['short'] in ['ИП', 'КФХ', 'ГКФХ']:
            ip_or_kfh = 'Да'

        full_name_leasee = result[0]['data']['name']['full_with_opf']

        full_krakt_name_leasee = result[0]['data']['name']['short_with_opf']

        if ip_or_kfh == 'Нет':
            inn_kpp_leasee = inn_leasee + '/' + result[0]['data']['kpp']
            leader_leasee = result[0]['data']['management']['post']
            fio_leader = result[0]['data']['management']['name']
        else:
            inn_kpp_leasee = inn_leasee
            type_business = result[0]['data']['opf']['short']
            leader_leasee = result[0]['data']['opf']['short']
            if result[0]['data']['opf']['short'] == 'ИП':
                leader_leasee = 'Индивидуальный предприниматель'
            else:
                leader_leasee = 'Глава'
            fio_leader = result[0]['data']['name']['full']

        last_name, first_name, patronymic_name = fio_leader.split()

        # Get the initial of the first name
        first_name_initial = first_name[0]

        # Get the initial of the patronymic name
        patronymic_initial = patronymic_name[0]

        # Combine the last name and initials in the desired format
        formatted_name_leader_leasee = f'{last_name} {first_name_initial}.{patronymic_initial}.'

        address_leasee = result[0]['data']['address']['unrestricted_value']

        ogrn_leasee = result[0]['data']['ogrn']

        okato_leasee = result[0]['data']['okato']

        okpo_leasee = result[0]['data']['okpo']

        # Значение registration_date в миллисекундах
        registration_date_ms = result[0]['data']['ogrn_date']
        # Преобразуем значение в объект datetime
        registration_date = datetime.datetime.fromtimestamp(registration_date_ms / 1000)
        # Преобразование строки в объект datetime
        date_time_obj = datetime.datetime.strptime(str(registration_date), "%Y-%m-%d %H:%M:%S")
        # Форматирование даты в нужный формат
        date_regist = date_time_obj.strftime("%d.%m.%Y")

        def parse_client_bs4(ogrn):
            nonlocal fio_list, inn_list, dolya_list, inn_dir_leasee, phone_leasee, email_leasee, main_activity_leasee, ustav_capital
            url = f'https://vbankcenter.ru/contragent/{ogrn}'
            url2 = f'https://vbankcenter.ru/contragent/search?searchStr={ogrn}'

            response = requests.get(url)
            response2 = requests.get(url2)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                soup2 = BeautifulSoup(response2.text, 'html.parser')

                if len(str(ogrn)) == 13:

                    try:
                        fio_list = list(map(lambda x: x.text, soup.find_all('h5', class_='text-base font-bold')))
                    except Exception as ex:
                        fio_list = ''
                        logging.info(ex, exc_info=True)

                    dolya_list = []
                    try:
                        for elem in soup.find_all('p', class_='text-base m-0 text-premium-600', string='Доля:'):
                            dolya_list.append(
                                "".join(elem.find_next('p', class_='text-base m-0 ml-1.5').text.split()[-1]).replace(
                                    '%',
                                    '').replace(
                                    '(', '').replace(')', ''))
                    except Exception as ex:
                        logging.info(ex, exc_info=True)

                    inn_list = []
                    try:
                        for elem in soup.find_all('p', class_='text-base m-0 text-premium-600', string='ИНН:'):
                            inn_list.append(elem.find_next('a', class_='flex text-base m-0 ml-1.5').text)
                    except Exception as ex:
                        logging.info(ex, exc_info=True)

                    try:
                        inn_dir_leasee = soup.find('p', class_='mb-1 whitespace-nowrap pr-6 text-premium-600').find('a',
                                                                                                                    class_='text-blue').text
                    except Exception as ex:
                        inn_dir_leasee = ''
                        logging.info(ex, exc_info=True)

                    try:
                        for elem in soup.find(class_='requisites-info-badge font-bold mb-1').find_next('div',
                                                                                                       class_='flex items-baseline mt-1').find(
                            class_='gweb-copy relative inline-block mb-0 py-0 copy-available z-10 cursor-pointer copy-right-padding'):
                            phone_leasee = elem.get_text(strip=True)
                    except Exception as ex:
                        phone_leasee = ''
                        logging.info('Нет телефона')
                        logging.info(ex, exc_info=True)

                    try:
                        for elem in soup.find(class_='requisites-info-badge font-bold mb-1').find_next('div',
                                                                                                       class_='flex items-baseline mt-1').find_next(
                            'div', class_='flex items-baseline mt-1').find('a'):
                            email_leasee = elem.get_text(strip=True)
                    except Exception as ex:
                        email_leasee = ''
                        logging.info('Нет email')
                        logging.info(ex, exc_info=True)

                    try:
                        main_activity_leasee = soup.find('a', class_='inline-block mt-1').get_text(strip=True)
                    except Exception as ex:
                        main_activity_leasee = ''
                        logging.info(ex, exc_info=True)

                    try:
                        number_element = soup2.find('span', class_='inline-block pr-2 text-premium-600 lg:mr-4 xl:mr-0',
                                                    string='Уставный капитал:').find_next_sibling('span')
                        number_text = number_element.text.strip()
                        ustav_capital = float(''.join(filter(lambda x: x.isdigit() or x == '.', number_text)))
                    except Exception as ex:
                        ustav_capital = ''
                        logging.info(ex, exc_info=True)

                else:
                    inn_dir_leasee = inn_leasee
                    phone_leasee = ''
                    email_leasee = ''
                    ustav_capital = ''
                    try:
                        main_activity_leasee = soup.find('a', class_='inline-block mt-1').get_text(strip=True)
                    except Exception as ex:
                        main_activity_leasee = ''
                        logging.info(ex, exc_info=True)

            else:
                logging.info(f"Ошибка при запросе: {response.status_code}")
                fio_list = ''
                dolya_list = []
                inn_list = []
                inn_dir_leasee = ''
                phone_leasee = ''
                email_leasee = ''
                ustav_capital = ''
                main_activity_leasee = ''

        parse_client_bs4(ogrn_leasee)

        logging.info(f"({current_user}) Этап 3.")