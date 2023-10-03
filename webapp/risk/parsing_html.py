import re
import json

from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from typing import List

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


def founders_physical(soup) -> dict:
    founders = {}

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-fl'
                             ).find_all('tr')
    except AttributeError as _ex:
        logging.info(_ex, exc_info=True)
        logging.info(f'Нет учредителей физ. лиц')
        return {}

    try:  # get director INN
        director_inn = director_inn_egrul(soup)[1]
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        director_inn = None

    try:
        for num, element in enumerate(elements, start=1):
            founders[num] = {}
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

            founders[num].setdefault('percent', percent)
            founders[num].setdefault('egrul', egrul)
            founders[num].setdefault('href', href)
            founders[num].setdefault('full_name', name)
            founders[num].setdefault('sum', sum_)
            founders[num].setdefault('inn', inn)
            founders[num].setdefault('mass_founder', mass_founder)
            founders[num].setdefault('director', director_inn == inn)

        return founders

    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return {}


def founders_legal(soup) -> dict:
    founders = {}

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-ul'
                             ).find_all('tr')
    except AttributeError as _ex:
        logging.info(f'Нет учредителей юр. лиц')
        return {}

    try:
        for num, element in enumerate(elements, start=1):
            founders[num] = {}
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

            founders[num].setdefault('percent', percent)
            founders[num].setdefault('egrul', egrul)
            founders[num].setdefault('href', href)
            founders[num].setdefault('name', name)
            founders[num].setdefault('sum', sum_)
            founders[num].setdefault('inn', inn)
            founders[num].setdefault('red_link', red_link)
            founders[num].setdefault('ogrn', ogrn)
            founders[num].setdefault('status', status)

        return founders

    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return {}


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
    fin = {}

    for year in [2022, 2021, 2020]:
        fin[year] = {}
        try:
            for element in soup.find('div', class_='financial-info', id=f'y_{year}'
                                     ).find_all('span', class_='cards__block-line'):
                try:
                    find_element = element.get_text(strip=True).split('—')
                    if element.find('i', class_='link-up'):
                        fin[year].setdefault(find_element[0].strip(), find_element[1].strip().removesuffix(
                            element.find('i', class_='link-up').get_text(strip=True)))
                    elif element.find('i', class_='link-down'):
                        fin[year].setdefault(find_element[0].strip(), find_element[1].strip().removesuffix(
                            element.find('i', class_='link-down').get_text(strip=True)))
                    else:
                        fin[year].setdefault(find_element[0].strip(), find_element[1].strip())
                except (AttributeError, TypeError, IndexError) as _ex:
                    logging.info('Ошибка в фин. показателях')
                    logging.info(_ex, exc_info=True)

        except (AttributeError, TypeError, IndexError) as _ex:
            logging.info(f'Нет информации по фин. показателям за {year}')
            logging.info(_ex, exc_info=True)

    return fin


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
        return soup.find('div', class_='card card-nopadding external-142 attached'
                         ).find('div', class_='card-section').get_text(strip=True, separator=' ')
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


def period_of_activity(soup):
    try:
        reg_comp_seller = dt.strptime(date_of_registration(soup), '%d.%m.%Y')
        cur_date_seller = dt.strptime(dt.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
        if relativedelta(cur_date_seller, reg_comp_seller).years >= 3:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def unprofitability(fin_func):
    try:
        if fin_func[2022]['Чистая прибыль'].startswith('-'):
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def inaccuracy_of_information(soup):
    try:
        if 'недостоверн' in soup.find(
                'div', class_='cards__column cards__column-first').get_text(' ', strip=True).lower():
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def mass_address(soup):
    try:
        if soup.find('div', class_='cards__column_block address_info').find('p', class_='link-red'):
            return 'Да'
        else:
            return 'Нет'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def extremism(soup):
    status = rosfinmonitoring(soup)
    try:
        if 'источнику отсутствует' in status or 'Запрос по источнику не отправлялся' in status:
            return 'Нет'
        else:
            return 'Да'
    except (AttributeError, TypeError, IndexError) as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def read_main_html(client_inn, object_inn, short_name):
    try:
        soup = BeautifulSoup(read_main_page(client_inn, object_inn, short_name), 'html.parser')
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
        'Менее 3х лет (да_нет)': period_of_activity(soup),  # for seller table
        'Убыточность (да_нет)': unprofitability(financial_statements(soup)),  # for seller table
        'Недостоверность сведений (да_нет)': inaccuracy_of_information(soup),  # for seller table
        'Массовый адрес (да_нет)': mass_address(soup),  # for seller table
        'Экстремизм (да_нет)': extremism(soup),  # for seller table
    }

    with open(f'main_info {object_inn}.json', 'a', encoding='utf-8') as file:
        json.dump(general_description_of_the_company, file, ensure_ascii=False, indent=3)
        file.write('\n')
        file.write('\n')
        file.write('=' * 70)
        file.write('\n')
        file.write('\n')

    return general_description_of_the_company


def read_main_html_individual(client_inn, object_inn, short_name):
    try:
        soup = BeautifulSoup(read_main_page(client_inn, object_inn, short_name), 'html.parser')
    except FileNotFoundError as _ex:
        logging.info(_ex, exc_info=True)
        raise _ex

    def ind_main_profile(title):
        try:
            status = soup.find('table', class_='cards__data contact_info').find('td', string=title).find_next(
                'td').get_text(' ', strip=True)
            logging.info(status)
            return status
        except (AttributeError, TypeError):
            logging.info(f'Не прожата кнопка для получения инфы по паспорту и тд. {title}')
            return '-'

    def ind_fio():
        try:
            status = ' '.join(soup.find('h2', class_='cards__company').find('span'
                                                                            ).get_text(' ', strip=True).split())
            logging.info(status)
            return status
        except (AttributeError, TypeError):
            logging.info('Не удалось получить ФИО')
            return '-'

    def ind_entrepreneur():
        try:
            len_ornip = len(
                soup.find('div',
                          class_='cards__column-container cards__column-container-first'
                          ).find_all('td', string='ОГРНИП:'))
        except (AttributeError, TypeError):
            len_ornip = 0
            logging.info('Нет данных по истории ИП/КФХ')

        info = {}
        if len_ornip > 0:
            for num in range(1, len_ornip + 1):
                info[num] = {}

                try:
                    date_of_reg = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find_all('td')[1].get_text(' ', strip=True)
                    info[num].setdefault('Дата регистрации ИП', date_of_reg)
                except (AttributeError, TypeError):
                    date_of_reg = '-'
                    info[num].setdefault('Дата регистрации ИП', date_of_reg)

                try:
                    date_of_liquidation = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='Дата прекращения деятельности:'
                                      ).find_next('td').get_text(' ', strip=True)
                    info[num].setdefault('Дата ликвидации ИП', date_of_liquidation)
                except (AttributeError, TypeError):
                    date_of_liquidation = '-'
                    info[num].setdefault('Дата ликвидации ИП', date_of_liquidation)

                try:
                    ogrnip = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='ОГРНИП:').find_next('td').get_text(' ', strip=True)
                    info[num].setdefault('ОГРНИП', ogrnip)
                except (AttributeError, TypeError):
                    ogrnip = '-'
                    info[num].setdefault('ОГРНИП', ogrnip)

                main_okved_value = '-'
                add_okveds_values = '-'

                try:
                    main_okved_value = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='ОКВЭД:').find_next('td').next_element.strip()
                    info[num].setdefault('Основной ОКВЭД', main_okved_value)

                except (AttributeError, TypeError):
                    info[num].setdefault('Основной ОКВЭД', main_okved_value)

                try:
                    add_okveds_values = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='ОКВЭД:').find_next('td').find_all_next('td')
                except (AttributeError, TypeError):
                    info[num].setdefault('Дополнительные ОКВЭД', add_okveds_values)

                add_okveds_list = []
                if add_okveds_values != '-':
                    for el in add_okveds_values:
                        if 'Статус' in el:
                            break
                        add_okveds_list.append(el.get_text(' ', strip=True))
                add_okveds_string = re.sub(r'(\d+)\n', r'\1 ', '\n'.join(add_okveds_list))
                info[num].setdefault('Дополнительные ОКВЭД', add_okveds_string)

                try:
                    status = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='Статус').find_next('td').get_text(' ', strip=True)
                    info[num].setdefault('Статус', status)
                except (AttributeError, TypeError):
                    status = '-'
                    info[num].setdefault('Статус', status)

        return info

    def ind_address():
        try:
            address = soup.find('h3',
                                class_='cards__subtitle', string='Адрес регистрации:'
                                ).find_next('div', class_='cards__column_block').get_text(
                ' ', strip=True).replace('посмотреть на карте', '')
            return address
        except (AttributeError, TypeError):
            logging.info('Нет удалось получить информацию по адресу регистрации')
            return '-'

    def ind_tax_authority():
        try:
            authority = soup.find('p', class_='cards__text cards__text-top').get_text('\n', strip=True)
            return authority
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по наименованию налогового органа')
            return '-'

    def ind_is_dir_or_founder_history():
        info = {}
        try:
            is_director = soup.find('div', class_='cards-directors'
                                    ).find_all('div', class_='company_more_info')
            info['Является руководителем'] = '\n'.join([el.get_text(' ', strip=True) for el in is_director])
        except (AttributeError, TypeError):
            info['Является руководителем'] = '-'

        try:
            is_founder = soup.find(
                'table',
                class_='cards__data cards__data-small cards__data-border founder-table cards-founders').find_all('tr')
            info['Является учредителем'] = '\n'.join([el.get_text(' ', strip=True) for el in is_founder])
        except (AttributeError, TypeError):
            info['Является учредителем'] = '-'

        try:
            was_director = soup.find('div', class_='directors-history'
                                     ).find_all('div', class_='company_more_info')
            info['Являлся руководителем'] = '\n'.join([el.get_text(' ', strip=True) for el in was_director])
        except (AttributeError, TypeError):
            info['Являлся руководителем'] = '-'

        try:
            was_founder = soup.find(
                'table',
                class_='founders-history cards__data cards__data-small cards__data-border founder-table').find_all(
                'tr')
            info['Являлся учредителем'] = '\n'.join([el.get_text(' ', strip=True) for el in was_founder])
        except (AttributeError, TypeError):
            info['Являлся учредителем'] = '-'

        return info

    def ind_arbit_cases():
        try:
            arbitrary = ' '.join(
                soup.find('div', class_='card card-nopadding external-139'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по арбитражным делам')
            arbitrary = '-'
        return arbitrary

    def ind_tax_debts():
        try:
            tax = ' '.join(
                soup.find('div', class_='card card-nopadding external-125'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по налоговой задолженности')
            tax = '-'
        return tax

    def ind_blocked_acc():
        try:
            blocked = ' '.join(
                soup.find('div', class_='card card-nopadding external-114'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по забл. расч. счетам')
            blocked = '-'
        return blocked

    def ind_fssp_fl():
        try:
            fssp = ' '.join(
                soup.find('div', class_='card card-nopadding external-35 attached').find('div',
                                                                                         class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по ФССП ФЛ')
            fssp = '-'
        return fssp

    def ind_reestr_zalog():
        try:
            reestr = ' '.join(
                soup.find('div', class_='card card-nopadding external-158').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по реестрам залогов')
            reestr = '-'
        return reestr

    def ind_fed_res():
        try:
            fed = ' '.join(
                soup.find('div', class_='card card-nopadding external-218').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по Фед Ресурсу')
            fed = '-'
        return fed

    def ind_narcos():
        try:
            narcos = ' '.join(
                soup.find('div', class_='card card-nopadding external-117').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по ГНК')
            narcos = '-'
        return narcos

    def ind_ros_fin():
        try:
            ros = ' '.join(
                soup.find('div', class_='card card-nopadding external-143').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по РОСФИНМОН')
            ros = '-'
        return ros

    def ind_sanc_usa():
        try:
            usa = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-sanction'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по санкциям')
            usa = '-'
        return usa

    def ind_justice():
        try:
            just = ' '.join(
                soup.find('div', class_='card card-nopadding external-164').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по Правосудие')
            just = '-'
        return just

    def ind_especially_reestr():
        try:
            especially = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-reestr'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по особым реестрам')
            especially = '-'
        return especially

    def ind_reestr_np():
        try:
            unscrupulous = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-rnp'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по РНП')
            unscrupulous = '-'
        return unscrupulous

    def ind_passport():
        try:
            passport = ' '.join(
                soup.find('div', class_='card card-nopadding external-175').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по паспорту РФ')
            passport = '-'
        return passport

    def ind_debtor():
        try:
            debtor = ' '.join(
                soup.find('div', class_='card card-nopadding external-50').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except (AttributeError, TypeError):
            logging.info('Не удалось получить информацию по Должнику')
            debtor = '-'
        return debtor

    def ind_inaccuracy_of_information():
        try:
            if 'недостоверн' in soup.find(
                    'div', class_='cards__column cards__column-first').get_text(' ', strip=True).lower():
                return 'Да'
            else:
                return 'Нет'
        except (AttributeError, TypeError, IndexError):
            return '-'

    def ind_period_of_activity():
        try:
            date_of_reg = soup.find('div', class_='cards__column cards__column-first').find_all('table', class_='cards__data')[1].find_all('td')[1].get_text(' ', strip=True)
        except (AttributeError, TypeError):
            date_of_reg = None

        if date_of_reg is not None:
            try:
                reg_comp_seller = dt.strptime(date_of_reg, '%d.%m.%Y')
                cur_date_seller = dt.strptime(dt.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
                if relativedelta(cur_date_seller, reg_comp_seller).years >= 3:
                    return 'Нет'
                else:
                    return 'Да'
            except (AttributeError, TypeError, IndexError):
                return '-'
        else:
            return '-'

    general_description_of_an_individual = {
        'Паспортные_данные': ind_main_profile('Паспорт:'),
        'Дата_рождения': ind_main_profile('Дата рождения:'),
        'Гражданство': ind_main_profile('Страна гражданства:'),
        'ИНН': ind_main_profile('ИНН:'),
        'ФИО': ind_fio(),
        'Инфо_ИП': ind_entrepreneur(),
        'Адрес_регистрации': ind_address(),
        'Имя_налог_органа': ind_tax_authority(),
        'История_руководства': ind_is_dir_or_founder_history(),
        'Арбитражные_дела': ind_arbit_cases(),
        'Налог_задолж': ind_tax_debts(),
        'Заблок_счета': ind_blocked_acc(),
        'ФССП_ФЛ': ind_fssp_fl(),
        'Реестр_залогов': ind_reestr_zalog(),
        'Фед_рес': ind_fed_res(),
        'ГНК': ind_narcos(),
        'РОС_ФИН': ind_ros_fin(),
        'Санкции': ind_sanc_usa(),
        'Правосудие': ind_justice(),
        'Особые_реестры': ind_especially_reestr(),
        'РНП': ind_reestr_np(),
        'Паспорт_РФ': ind_passport(),
        'Должник': ind_debtor(),
        'Недостоверность сведений (да_нет)': ind_inaccuracy_of_information(),
        'Менее 3 лет (да_нет)': ind_period_of_activity(),
    }

    with open(f'physic_info {object_inn}.json', 'a', encoding='utf-8') as file:
        json.dump(general_description_of_an_individual, file, ensure_ascii=False, indent=3)
        file.write('\n')
        file.write('\n')
        file.write('=' * 70)
        file.write('\n')
        file.write('\n')

    return general_description_of_an_individual
