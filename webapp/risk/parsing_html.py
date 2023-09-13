import re
import sys
import time
import json

from bs4 import BeautifulSoup
from typing import List
from pprint import pprint

from webapp.risk.download_page import read_main_page
from webapp.risk.logger import logging
from webapp.risk.models import Okved


def full_name_company(soup):
    try:
        return soup.find('p', class_='cards__text cards__text-margin').get_text(strip=True)
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def short_name_company(soup):
    try:
        return soup.find('h2', class_='cards__company').find('span').get_text(strip=True)
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def company_status(soup):
    if soup.find('span', class_='cards__status cards__status-green') is not None:
        return soup.find('span', class_='cards__status cards__status-green').get_text(strip=True).replace(
            'По данным ФНС:', '')
    elif soup.find('span', class_='cards__status cards__status-red') is not None:
        return soup.find('span', class_='cards__status cards__status-red').get_text(strip=True).replace(
            'По данным ФНС:', '')

    logging.info('Не удалось получить СТАТУС компании')
    return '-'


def company_inn_kpp_ogrn_okpo(soup, kpp_inn_okpo):
    rows = soup.find('table', class_='cards__data').find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        try:
            if len(cells) == 2 and kpp_inn_okpo in cells[0].get_text(strip=True):
                return cells[1].get_text(strip=True)
        except (AttributeError, TypeError) as _ex:
            logging.info(_ex, exc_info=True)
            return '-'

    logging.info(f'Не удалось получить {kpp_inn_okpo} компании')
    return '-'


def date_of_registration(soup):
    elements = soup.find_all('h3', class_='cards__subtitle')

    for element in elements:
        if "Дата регистрации:" in element.get_text():
            date_element = element.find('span')
            if date_element:
                registration_date = date_element.get_text(strip=True)
                return registration_date

    else:
        logging.info(f'Не удалось получить ДАТА РЕГИСТРАЦИИ компании')
        return '-'


def legal_address(soup):
    try:
        return soup.find('span', class_='find_address cards__column_block-link').get_text(strip=True)
    except (AttributeError, TypeError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def pfr(soup):
    try:
        return soup.find('tr', title='Пенсионный фонд России').find_all('td')[1].get_text(strip=True)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def fss(soup):
    try:
        return soup.find('tr', title='Social Insurance Fund').find_all('td')[1].get_text(strip=True)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_name(soup):
    try:
        return soup.find('div', 'cards__text cards__text-top').find('a', class_='cards__column_block-link').get_text(
            strip=True)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_href(soup):
    try:
        return soup.find('div', 'cards__text cards__text-top').find('a', class_='cards__column_block-link')['href']
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_inn_egrul(soup) -> List[str]:
    try:
        elements = soup.find('div', 'cards__text cards__text-top').find_all('span', class_='cards__column-small')
        return [element.get_text() for element in elements]
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def authorized_capital(soup):
    elements = soup.find('div', class_='cards__column cards__column-first').find_all('div',
                                                                                     class_='cards__column_block')
    text = ''
    pattern = r'(\d[\d\s]+руб\.)'

    for element in elements:
        if 'Уставный капитал' in element.get_text(strip=True):
            text = element.get_text(strip=True, separator=' ').removeprefix('Уставный капитал: ')

    match = re.search(pattern, text)

    if match:
        return match.group(1)
    else:
        logging.info(f'Не удалось получить УСТАВНЫЙ КАПИТАЛ компании')
        return '-'


def main_activity(soup):
    try:
        code = soup.find('table', class_='cards__data-small').find_all('tr')[0].find('td').get_text(strip=True)
        return Okved.return_okved_name(code)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def temporary_func(soup):  # Временная функция для проверки кода ОКВЭД
    try:
        return soup.find(
            'span', class_='cards__column_block-link cards__column_more-link appear'
        ).find_previous('table', class_='cards__data cards__data-small').find('td').get_text(strip=True)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def additional_activities(soup) -> List[str]:
    try:
        elements = soup.find('table', class_='cards__data-small cards__data-nomargin cards__column_hidden').find_all(
            'tr')
        return [element.get_text(strip=True, separator=' ') for element in elements]
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def founders_physical(soup) -> List[dict]:
    list_of_founders = []

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-fl'
                             ).find_all('tr')
    except AttributeError as _ex:
        logging.info(_ex, exc_info=True)
        logging.info(f'Нет учредителей физ. лиц')
        return []

    try:  # get director INN
        director_inn = director_inn_egrul(soup)[1]
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        director_inn = None

    try:
        for num, element in enumerate(elements, start=1):
            percent = element.find('td').get_text(strip=True) if element.find('td') else ''
            egrul = element.find(
                'div', class_='division').find('span', class_='cards__column-small').get_text(strip=True
                                                                                              ) if element.find(
                'div', class_='division').find('span', class_='cards__column-small') else ''
            href = element.find(
                'div', class_='division').find('a', class_='cards__column_block-link')['href'] if element.find(
                'div', class_='division').find('a', class_='cards__column_block-link') else ''
            name = element.find(
                'div', class_='division').find('a', class_='cards__column_block-link').get_text(strip=True
                                                                                                ) if element.find(
                'div', class_='division').find('a', class_='cards__column_block-link') else ''
            try:
                sum_ = re.sub(r'\s+', ' ', element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[1].get_text(strip=True)) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[1] else ''
            except IndexError:
                sum_ = ''
            try:
                inn = element.find(
                    'div', class_='division').find_all('span', class_='cards__column-small'
                                                       )[2].get_text(strip=True) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[2] else ''
            except IndexError:
                inn = ''
            mass_founder = element.find(
                'div', class_='division').find('div', class_='link-red').get_text(strip=True
                                                                                  ) if element.find(
                'div', class_='division').find('div', class_='link-red') else ''

            list_of_founders.append({
                'number': num,
                'percent': percent,
                'egrul': egrul,  # формат 'ЕГРЮЛ 13.09.2013'
                'href': href,  # формат '/summary/person/3866936-163501570209'
                'name': name,
                'sum': sum_,
                'inn': inn,  # формат 'ИНН 163501570209'
                'mass founder': mass_founder,  # смотрит есть ли красный линк у учредителя
                # (Пример red-link: По данным ФНС является массовым учредителем.'
                'director': director_inn == inn  # сравнение ИНН учредителя с ИНН директора
            })
        return list_of_founders

    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return []


def founders_legal(soup) -> List[dict]:
    list_of_founders = []

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-ul'
                             ).find_all('tr')
    except AttributeError as _ex:
        logging.info(f'Нет учредителей юр. лиц')
        return []

    try:
        for num, element in enumerate(elements, start=1):
            percent = element.find('td').get_text(strip=True) if element.find('td') else ''
            try:
                sum_ = re.sub(r'\s+', ' ',
                              element.find('div', class_='division').find_all('span', class_='cards__column-small'
                                                                              )[0].get_text(strip=True)) if \
                    element.find('div', class_='division').find_all(
                        'span', class_='cards__column-small')[0] else ''
            except IndexError:
                sum_ = ''
            try:
                egrul = element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[1].get_text(
                    strip=True) if element.find('div', class_='division').find_all(
                    'span', class_='cards__column-small')[1] else ''
            except IndexError:
                egrul = ''
            href = element.find(
                'div', class_='division').find('a', class_='cards__column_block-link open-card'
                                               )['href'] if element.find(
                'div', class_='division').find('a', class_='cards__column_block-link open-card') else ''
            name = element.find(
                'div', class_='division').find(
                'a', class_='cards__column_block-link open-card'
            ).get_text(strip=True) if element.find(
                'div', class_='division').find('a', class_='cards__column_block-link open-card') else ''

            if element.find('div', class_='division').find(
                    'span', class_='cards__status cards__status_description cards__status-green'):
                status = element.find(
                    'div', class_='division').find(
                    'span', class_='cards__status cards__status_description cards__status-green').get_text(strip=True)
            elif element.find('div', class_='division'
                              ).find('span', class_='cards__status cards__status_description cards__status-orange'):
                status = element.find(
                    'div', class_='division').find(
                    'span', class_='cards__status cards__status_description cards__status-orange').get_text(strip=True)
            elif element.find('div', class_='division'
                              ).find('span', class_='cards__status cards__status_description cards__status-red'):
                status = element.find('div', class_='division'
                                      ).find('span', class_='cards__status cards__status_description cards__status-red'
                                             ).get_text(strip=True)
            else:
                status = ''

            try:
                inn = element.find(
                    'div', class_='division').find_all('span', class_='cards__column-small'
                                                       )[2].get_text(strip=True) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[2] else ''
            except IndexError:
                inn = ''

            try:
                ogrn = element.find(
                    'div', class_='division').find_all('span', class_='cards__column-small'
                                                       )[3].get_text(strip=True) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[3] else ''
            except IndexError:
                ogrn = ''

            red_link = element.find(
                'div', class_='division').find('div', class_='link-red').get_text(strip=True
                                                                                  ) if element.find(
                'div', class_='division').find('div', class_='link-red') else ''

            list_of_founders.append({
                'number': num,
                'percent': percent,
                'egrul': egrul,  # формат 'ЕГРЮЛ 13.09.2013'
                'href': href,  # формат '/summary/company/5468450-1655087607'
                'name': name,
                'sum': sum_,
                'inn': inn,  # формат 'ИНН 163501570209'
                'red-link': red_link,  # смотрит есть ли красный линк (негатив) у учредителя юр лица
                'ogrn': ogrn,  # формат 'ОГРН ...'
                'status': status
            })
        return list_of_founders

    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return []


def blocked_current_accounts(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-111'
                         ).find('div', class_='card-section').find('span').get_text(strip=True)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def tax_debts(soup) -> List[str]:
    links = []
    try:
        link_green = soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}
        ).find('p', class_='link-green').get_text(strip=True, separator=' ').replace('\n', ' ').replace('  ', '')
        links.append(link_green)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info('Нет зеленого линка у компании по налогам')

    try:
        link_orange = soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}
        ).find('p', class_='link-orange').get_text(strip=True, separator=' ').replace('\n', ' ').replace('  ', '')
        links.append(link_orange)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info('Нет оранжевого линка у компании по налогам')

    try:
        link_red = soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}
        ).find('p', class_='link-red').get_text(strip=True, separator=' ').replace('\n', ' ').replace('  ', '')
        if 'По данным ФНС на дату' not in link_red:
            links.append(link_red)
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info('Нет красного линка у компании по налогам')

    return links


def count_of_members(soup) -> List[str]:
    members_list = []
    try:
        elements = soup.find('div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}).find_all('p')
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']
    for element in elements:
        if 'По данным ФНС' in element.get_text(strip=True, separator=' '):
            members_list.append(element.get_text(strip=True, separator=' ').replace('\n', ' ').replace('  ', ''))
    return members_list


def history(soup):
    try:
        elements = soup.find('div', class_='card-wrapper'
                             ).get_text(strip=True, separator='|').replace('\n', ' '
                                                                           ).replace('  ', '').replace('|', '\n')
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return 'Отсутствует какая-либо история изменений'

    return elements


def financial_statements(soup):
    fin_list = []

    for year in [2022, 2021, 2020]:
        indicators = {}
        try:
            for element in soup.find('div', class_='financial-info', id=f'y_{year}'
                                     ).find_all('span', class_='cards__block-line'):
                try:
                    find_element = element.get_text(strip=True).split('—')
                    if element.find('i', class_='link-up'):
                        indicators[find_element[0].strip()] = find_element[1].strip().removesuffix(
                            element.find('i', class_='link-up').get_text(strip=True))
                    elif element.find('i', class_='link-down'):
                        indicators[find_element[0].strip()] = find_element[1].strip().removesuffix(
                            element.find('i', class_='link-down').get_text(strip=True))
                    else:
                        indicators[find_element[0].strip()] = find_element[1].strip()
                except (AttributeError, TypeError, IndexError) as _ex:
                    logging.info('Ошибка в фин. показателях')
                    logging.info(_ex, exc_info=True)

            fin_list.append(
                {
                    year: indicators
                }
            )
        except (AttributeError, TypeError, IndexError) as _ex:
            logging.info(f'Нет информации по фин. показателям за {year}')
            logging.info(_ex, exc_info=True)

    return fin_list


def taxes_and_fees(soup):
    try:
        taxes_list = []
        elements = soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-taxees-fees'}
        ).find('div', class_='card-section').find_all('p')
        try:
            for element in elements:
                taxes_list.append(element.get_text(strip=True, separator=' ').replace('\n', ' ').replace('  ', ''))
            return taxes_list
        except (AttributeError, TypeError, IndexError) as _ex:
            logging.info(_ex, exc_info=True)

    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return []


def federal_resource(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-217').find('div', class_='card-section').get_text(
            strip=True, separator=' ').removesuffix('Подробнее').strip()
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def register_of_pledges(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-157').find('div', class_='card-section').get_text(
            strip=True, separator=' ').removesuffix('Подробнее').removesuffix('Предыдущие данные').strip()
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def rosfinmonitoring(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-142 attached').find('div',
                                                                                         class_='card-section').get_text(
            strip=True, separator=' ')
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def sanctions(soup):
    try:
        return soup.find('div', class_='card card-nopadding',
                         attrs={'data-element': 'local-sanction'}).find('div', class_='card-section').get_text(
            strip=True, separator=' ')
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def get_url_delta(soup):
    try:
        return soup.find('div', class_='card card-nopadding',
                         attrs={'data-element': 'local-analitic'}).find('a', class_="cards__column_block-link")['href']
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def read_main_html(client_inn, object_inn):
    try:
        soup = BeautifulSoup(read_main_page(client_inn, object_inn), 'html.parser')
    except FileNotFoundError as _ex:
        logging.info(_ex, exc_info=True)
        raise _ex

    general_description_of_the_company = {
        'Полное наименование': full_name_company(soup),
        'Краткое наименование': short_name_company(soup),
        'Статус': company_status(soup),
        'ИНН': company_inn_kpp_ogrn_okpo(soup, 'ИНН:'),
        'КПП': company_inn_kpp_ogrn_okpo(soup, 'КПП:'),
        'ОГРН': company_inn_kpp_ogrn_okpo(soup, 'ОГРН:'),
        'ОКПО': company_inn_kpp_ogrn_okpo(soup, 'ОКПО:'),
        'Дата регистрации': date_of_registration(soup),
        'Юр. адрес': legal_address(soup),
        'Налоговая задолженность': '\n'.join(tax_debts(soup)),
        'Заблокированные р. сч.': blocked_current_accounts(soup),
        'ПФР': pfr(soup),
        'ФСС': fss(soup),
        'ГЕНЕРАЛЬНЫЙ ДИРЕКТОР/ДИРЕКТОР': director_name(soup),
        'ЕГРЮЛ/ИНН ДИРЕКТОРА': director_inn_egrul(soup),
        'ССЫЛКА НА ДИРЕКТОРА': director_href(soup),
        'УЧРЕДИТЕЛИ ЮЛ': founders_legal(soup),
        'УЧРЕДИТЕЛИ ФЛ': founders_physical(soup),
        'Уставный капитал': authorized_capital(soup),
        'Основной вид деятельности': temporary_func(soup),
        f'Доп. виды деятельности ({len(additional_activities(soup))})': '\n'.join(additional_activities(soup)),
        'Кол-во сотрудников': '\n'.join(count_of_members(soup)),
        'ИСТОРИЯ': history(soup),
        'Финансы': financial_statements(soup),
        'Налоги и сборы': '\n'.join(taxes_and_fees(soup)),
        'Федресурс': federal_resource(soup),
        'Реестр залогов': register_of_pledges(soup),
        'Росфинмониторинг': rosfinmonitoring(soup),
        'Санкции': sanctions(soup),
        'Черный список': 'Информация по источнику отсутствует',
        'URL_Delta': get_url_delta(soup),
    }


    # with open('for_test.json', 'a', encoding='utf-8') as file:
    #     json.dump(general_description_of_the_company, file, ensure_ascii=False, indent=3)
    #     file.write('\n')
    #     file.write('\n')
    #     file.write('=' * 70)
    #     file.write('\n')
    #     file.write('\n')
    return general_description_of_the_company

# read_main_html('1684000880', '1635010074')
# read_main_html('1684000880', '1635011046')
# read_main_html('1684000880', '1661065440')
# read_main_html('1684000880', '1684000880')
# read_main_html('1684000880', '1659189303')
# read_main_html('1684000880', '5257208909')
# read_main_html('1684000880', '1655099271')
# read_main_html('1684000880', '1655443020')
# read_main_html('1684000880', '1659110896')
# read_main_html('1684000880', '5258064400')
# read_main_html('1684000880', '7203519669')
# read_main_html('1684000880', '7729588182')
# sys.exit()
