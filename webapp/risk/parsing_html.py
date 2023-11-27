import re

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
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def short_name_company(soup):
    try:
        return soup.find('h2', class_='cards__company').find('span').get_text(strip=True)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def company_status(soup):
    try:
        if soup.find('span', class_='cards__status cards__status-green') is not None:
            return soup.find('span', class_='cards__status cards__status-green').get_text(strip=True).replace(
                'По данным ФНС:', '')
        elif soup.find('span', class_='cards__status cards__status-red') is not None:
            return soup.find('span', class_='cards__status cards__status-red').get_text(strip=True).replace(
                'По данным ФНС:', '')

    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def company_inn_kpp_ogrn_okpo(soup, kpp_inn_okpo):
    rows = soup.find(class_='cards__data').find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        try:
            if len(cells) == 2 and kpp_inn_okpo in cells[0].get_text(strip=True):
                return cells[1].get_text(strip=True)
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return '-'

    logging.info(f'Не удалось получить {kpp_inn_okpo} компании')
    return '-'


def date_of_registration(soup):
    try:
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
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def legal_address(soup):
    try:
        return soup.find('span', class_='find_address cards__column_block-link').get_text(strip=True)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def pfr(soup):
    try:
        return soup.find('tr', title='Пенсионный фонд России').find_all('td')[1].get_text(strip=True)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def fss(soup):
    try:
        return soup.find('tr', title='Social Insurance Fund').find_all('td')[1].get_text(strip=True)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_name(soup):
    try:
        return soup.find('div', 'cards__text cards__text-top').find('a', class_='cards__column_block-link').get_text(
            strip=True)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_href(soup):
    try:
        return soup.find('div', 'cards__text cards__text-top').find('a', class_='cards__column_block-link')['href']
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def director_inn_egrul(soup) -> List[str]:
    try:
        elements = soup.find('div', 'cards__text cards__text-top').find_all('span', class_='cards__column-small')
        return [element.get_text() for element in elements]
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def authorized_capital(soup):
    try:
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
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def main_activity(soup):
    try:
        code = soup.find(class_='cards__column_block-link cards__column_more-link appear').parent.parent.parent.find(
            'td').get_text(strip=True)
        logging.info(Okved.return_okved_name(code))
        return Okved.return_okved_name(code)
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def additional_activities(soup) -> List[str]:
    try:
        elements = soup.find('table', class_='cards__data-small cards__data-nomargin cards__column_hidden').find_all(
            'tr')
        return [element.get_text(strip=True, separator=' ') for element in elements]
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def founders_physical(soup) -> dict:
    founders = {}

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-fl'
                             ).find_all('tr')
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        logging.info(f'Нет учредителей физ. лиц')
        return {}

    try:  # get director INN
        director_inn = director_inn_egrul(soup)[1]
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        director_inn = None

    try:
        for num, element in enumerate(elements, start=1):
            founders[num] = {}
            percent = element.find('td').get_text(strip=True) if element.find('td') else ''
            try:
                egrul = element.find(
                    'div', class_='division').find('span', class_='cards__column-small').get_text(strip=True
                                                                                                  ) if element.find(
                    'div', class_='division').find('span', class_='cards__column-small') else ''
            except Exception:
                egrul = ''
            try:
                href = element.find(
                    'div', class_='division').find('a', class_='cards__column_block-link')['href'] if element.find(
                    'div', class_='division').find('a', class_='cards__column_block-link') else ''
            except Exception:
                href = ''
            try:
                name = element.find(
                    'div', class_='division').find('a', class_='cards__column_block-link').get_text(strip=True
                                                                                                    ) if element.find(
                    'div', class_='division').find('a', class_='cards__column_block-link') else ''
            except Exception:
                name = ''
            try:
                sum_ = re.sub(r'\s+', ' ', element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[1].get_text(strip=True)) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[1] else ''
            except Exception:
                sum_ = ''
            try:
                inn = element.find(
                    'div', class_='division').find_all('span', class_='cards__column-small'
                                                       )[2].get_text(strip=True) if element.find(
                    'div', class_='division').find_all(
                    'span', class_='cards__column-small')[2] else ''
            except Exception:
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

    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return {}


def founders_legal(soup) -> dict:
    founders = {}

    try:
        elements = soup.find('table',
                             class_='cards__data cards__data-small cards__data-border founder-table founder-table-ul'
                             ).find_all('tr')
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
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
            founders[num].setdefault('full_name', name)
            founders[num].setdefault('sum', sum_)
            founders[num].setdefault('inn', inn)
            founders[num].setdefault('red_link', red_link)
            founders[num].setdefault('ogrn', ogrn)
            founders[num].setdefault('status', status)

        return founders

    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return {}


def blocked_current_accounts(soup):
    try:
        return " ".join(soup.find('div', class_='card card-nopadding external-111'
                                  ).find('div', class_='card-section').find('span').get_text(strip=True).split())
    except Exception as _ex:
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
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        logging.info('Нет оранжевого линка у компании по налогам')

    try:
        link_red = soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}
        ).find_all('p', class_='link-red')
        logging.info(link_red)
        for elem in link_red:
            if 'По данным ФНС на дату' not in " ".join(elem.get_text(strip=True, separator=' ').split()):
                links.append(" ".join(elem.get_text(strip=True, separator=' ').split()))

    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        logging.info('Нет красного линка у компании по налогам')

    try:
        tax_arrears = ' '.join(soup.find(
            'div', class_='card card-nopadding', attrs={'data-element': 'local-tax-penalty'}
        ).find('div', class_='card-section').find('p').get_text(strip=True, separator=' ').split())
        links.append(f'Налоговые недоимки: {tax_arrears}')
    except Exception as _ex:
        logging.info(_ex, exc_info=True)

    logging.info(links)
    return links


def count_of_members(soup) -> List[str]:
    members_list = []
    try:
        elements = soup.find('div', class_='card card-nopadding', attrs={'data-element': 'local-reestr'}).find_all('p')
    except Exception as _ex:
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
    except Exception as _ex:
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

        except Exception as _ex:
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
            if len(taxes_list) > 0:
                return taxes_list
            else:
                return ['Информация не найдена']
        except (AttributeError, TypeError, IndexError) as _ex:
            logging.info(_ex, exc_info=True)

    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return ['-']


def federal_resource(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-217').find('div', class_='card-section').get_text(
            strip=True, separator=' ').removesuffix('Подробнее').strip()
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def register_of_pledges(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-157').find('div', class_='card-section').get_text(
            strip=True, separator=' ').removesuffix('Подробнее').removesuffix('Предыдущие данные').strip()
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def rosfinmonitoring(soup):
    try:
        return soup.find('div', class_='card card-nopadding external-142'
                         ).find('div', class_='card-section').get_text(strip=True, separator=' ')
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return 'Информация по источнику отсутствует'


def sanctions(soup):
    try:
        return soup.find('div', class_='card card-nopadding',
                         attrs={'data-element': 'local-sanction'}).find('div', class_='card-section').get_text(
            strip=True, separator=' ')
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return 'Информация по источнику отсутствует'


def get_url_delta(soup):
    try:
        return soup.find('div', class_='card card-nopadding',
                         attrs={'data-element': 'local-analitic'}).find('a', class_="cards__column_block-link")['href']
    except Exception as _ex:
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
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def unprofitability(fin_func):
    try:
        if fin_func.get(2022):
            if fin_func[2022].get('Чистая прибыль', '').startswith('-'):
                return 'Да'
            else:
                return 'Нет'
        else:
            return 'Нет'
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def inaccuracy_of_information(soup):
    try:
        if 'недостоверн' in soup.find(
                'div', class_='cards__column cards__column-first').get_text(' ', strip=True).lower():
            return 'Да'
        else:
            return 'Нет'
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def mass_address(soup):
    try:
        if soup.find('div', class_='cards__column_block address_info').find('p', class_='link-red'):
            return 'Да'
        else:
            return 'Нет'
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def extremism(soup):
    status = rosfinmonitoring(soup)
    try:
        if 'источнику отсутствует' in status or 'Запрос по источнику не отправлялся' in status:
            return 'Нет'
        else:
            return 'Да'
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def affiliated_companies(soup):
    try:
        return " ".join(soup.find('div', class_='card card-nopadding',
                                  attrs={'data-element': 'local-founded-companies'}).find('div',
                                                                                          class_='card-section').get_text(
            ' ', strip=True).split())
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        return '-'


def read_main_html(client_inn, object_inn, short_name):
    try:
        soup = BeautifulSoup(read_main_page(client_inn, object_inn, short_name), 'html.parser')
    except Exception as _ex:
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
        'ЕГРЮЛ/ИНН ДИРЕКТОРА': " ".join(director_inn_egrul(soup)),
        'УЧРЕДИТЕЛИ ЮЛ': founders_legal(soup),
        'УЧРЕДИТЕЛИ ФЛ': founders_physical(soup),
        'Уставный капитал': authorized_capital(soup),
        'Основной вид деятельности': main_activity(soup),
        f'Доп. виды деятельности ({len(additional_activities(soup))})': '\n'.join(additional_activities(soup)),
        'Кол-во сотрудников': '\n'.join(count_of_members(soup)),
        'ИСТОРИЯ': history(soup),
        'ССЫЛКА НА ДИРЕКТОРА': director_href(soup),
        'Финансы': financial_statements(soup),
        'Дочерние организации': affiliated_companies(soup),
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
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info(f'Не прожата кнопка для получения инфы по паспорту и тд. {title}')
            return '-'

    def ind_fio():
        try:
            status = ' '.join(soup.find('h2', class_='cards__company').find('span'
                                                                            ).get_text(' ', strip=True).split())
            logging.info(status)
            return status
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить ФИО')
            return '-'

    def ind_entrepreneur():
        try:
            len_ornip = len(
                soup.find('div',
                          class_='cards__column-container cards__column-container-first'
                          ).find_all('td', string='ОГРНИП:'))
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
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
                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
                    date_of_reg = '-'
                    info[num].setdefault('Дата регистрации ИП', date_of_reg)

                try:
                    date_of_liquidation = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='Дата прекращения деятельности:'
                                      ).find_next('td').get_text(' ', strip=True)
                    info[num].setdefault('Дата ликвидации ИП', date_of_liquidation)
                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
                    date_of_liquidation = '-'
                    info[num].setdefault('Дата ликвидации ИП', date_of_liquidation)

                try:
                    ogrnip = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='ОГРНИП:').find_next('td').get_text(' ', strip=True)
                    info[num].setdefault('ОГРНИП', ogrnip)
                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
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

                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
                    info[num].setdefault('Основной ОКВЭД', main_okved_value)

                try:
                    add_okveds_values = \
                        soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                              class_='cards__data')[
                            num].find('td', string='ОКВЭД:').find_next('td').find_all_next('td')
                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
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
                except Exception as _ex:
                    logging.info(_ex, exc_info=True)
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
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Нет удалось получить информацию по адресу регистрации')
            return '-'

    def ind_tax_authority():
        try:
            authority = soup.find('p', class_='cards__text cards__text-top').get_text('\n', strip=True)
            return authority
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по наименованию налогового органа')
            return '-'

    def ind_is_dir_or_founder_history():
        info = {}
        try:
            is_director = soup.find('div', class_='cards-directors'
                                    ).find_all('div', class_='company_more_info')
            info['Является руководителем'] = '\n'.join([el.get_text(' ', strip=True) for el in is_director])
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            info['Является руководителем'] = '-'

        try:
            is_founder = soup.find(
                'table',
                class_='cards__data cards__data-small cards__data-border founder-table cards-founders').find_all('tr')
            info['Является учредителем'] = '\n'.join([el.get_text(' ', strip=True) for el in is_founder])
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            info['Является учредителем'] = '-'

        try:
            was_director = soup.find('div', class_='directors-history'
                                     ).find_all('div', class_='company_more_info')
            info['Являлся руководителем'] = '\n'.join([el.get_text(' ', strip=True) for el in was_director])
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            info['Являлся руководителем'] = '-'

        try:
            was_founder = soup.find(
                'table',
                class_='founders-history cards__data cards__data-small cards__data-border founder-table').find_all(
                'tr')
            info['Являлся учредителем'] = '\n'.join([el.get_text(' ', strip=True) for el in was_founder])
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            info['Являлся учредителем'] = '-'

        return info

    def ind_arbit_cases():
        try:
            arbitrary = ' '.join(
                soup.find('div', class_='card card-nopadding external-139'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по арбитражным делам')
            arbitrary = '-'
        return arbitrary

    def ind_arbit_cases_ip():
        try:
            arbitrary = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-arbitr'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по арбитражным делам')
            arbitrary = '-'
        return arbitrary

    def ind_tax_debts():
        try:
            tax = ' '.join(
                soup.find('div', class_='card card-nopadding external-125'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по налоговой задолженности')
            tax = '-'
        return tax

    def ind_blocked_acc():
        try:
            blocked = ' '.join(
                soup.find('div', class_='card card-nopadding external-114'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по забл. расч. счетам')
            blocked = '-'
        return blocked

    def ind_fssp_fl():
        try:
            fssp = ' '.join(
                soup.find('div', class_='card card-nopadding external-35 attached').find('div',
                                                                                         class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по ФССП ФЛ')
            fssp = '-'
        return fssp

    def ind_reestr_zalog():
        try:
            reestr = ' '.join(
                soup.find('div', class_='card card-nopadding external-158').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по реестрам залогов')
            reestr = '-'
        return reestr

    def ind_fed_res():
        try:
            fed = ' '.join(
                soup.find('div', class_='card card-nopadding external-218').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по Фед Ресурсу')
            fed = '-'
        return fed

    def ind_narcos():
        try:
            narcos = ' '.join(
                soup.find('div', class_='card card-nopadding external-117').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по ГНК')
            narcos = '-'
        return narcos

    def ind_ros_fin():
        try:
            ros = ' '.join(
                soup.find('div', class_='card card-nopadding external-143').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по РОСФИНМОН')
            ros = '-'
        return ros

    def ind_sanc_usa():
        try:
            usa = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-sanction'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по санкциям')
            usa = '-'
        return usa

    def ind_justice():
        try:
            just = ' '.join(
                soup.find('div', class_='card card-nopadding external-164').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по Правосудие')
            just = '-'
        return just

    def ind_especially_reestr():
        try:
            especially = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-reestr'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по особым реестрам')
            especially = '-'
        return especially

    def ind_reestr_np():
        try:
            unscrupulous = ' '.join(
                soup.find('div', class_='card card-nopadding',
                          attrs={'data-element': 'local-rnp'}).find('div', class_='card-section').get_text(
                    ' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по РНП')
            unscrupulous = '-'
        return unscrupulous

    def ind_passport():
        try:
            passport = ' '.join(
                soup.find('div', class_='card card-nopadding external-175').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по паспорту РФ')
            passport = '-'
        return passport

    def ind_debtor():
        try:
            debtor = ' '.join(
                soup.find('div', class_='card card-nopadding external-50').find('div', class_='card-section').find(
                    'span').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
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
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return '-'

    def ind_period_of_activity():
        try:
            date_of_reg = \
                soup.find('div', class_='cards__column cards__column-first').find_all('table', class_='cards__data')[
                    1].find_all('td')[1].get_text(' ', strip=True)
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            date_of_reg = None

        if date_of_reg is not None:
            try:
                reg_comp_seller = dt.strptime(date_of_reg, '%d.%m.%Y')
                cur_date_seller = dt.strptime(dt.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
                if relativedelta(cur_date_seller, reg_comp_seller).years >= 3:
                    return 'Нет'
                else:
                    return 'Да'
            except Exception as _ex:
                logging.info(_ex, exc_info=True)
                return '-'
        else:
            return '-'

    def ind_mass_address():
        try:
            if soup.find('h3', class_='cards__subtitle', string='Адрес регистрации:').find_next('div',
                                                                                                class_='cards__column_block').find(
                'p', class_='link-red'):
                return 'Да'
            else:
                return 'Нет'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Адрес не массовый')
            return 'Нет'

    def ind_bankrupt_notices():
        try:
            if soup.find('div', class_='card card-nopadding',
                         attrs={'data-element': 'local-bankrupt'}).find('div', class_='card-section').get_text(
                strip=True, separator=' ') in ['Информация не найдена', 'Информация по источнику отсутствует',
                                               'Информация по данному источнику отсутствует', 'Запрос обрабатывается']:
                return 'Нет'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'

    def ind_liquid():
        try:
            if soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                     class_='cards__data')[
                1].find('td', string='Статус').find_next('td').get_text(' ',
                                                                        strip=True) == 'Индивидуальный предприниматель прекратил деятельность в связи с принятием им соответствующего решения':
                return 'Да'
            else:
                return 'Нет'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'

    def ind_bankrupt():
        try:
            if 'банкрот' in soup.find('div', class_='cards__column cards__column-first').find_all('table',
                                                                                                  class_='cards__data')[
                1].find('td', string='Статус').find_next('td').get_text(' ', strip=True).lower():
                return 'Да'
            else:
                return 'Нет'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'

    def ind_arbitr():
        try:
            list_arbitr = soup.find('div', class_='card card-nopadding',
                                    attrs={'data-element': 'local-arbitr'}).find_all('a')
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'
        try:
            for elem in list_arbitr:
                if 'ответчик' == elem.get_text(' ', strip=True).lower():
                    return 'Да'
            return 'Нет'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'

    def ind_fssp():
        try:
            fssp = ' '.join(
                soup.find('div', class_='card card-nopadding external-35 attached'
                          ).find('div', class_='card-section').find('span').get_text(' ', strip=True).split())
            match = re.search(r'(\d+)\s+руб(?:л[ей|я])', fssp)
            logging.info(fssp)
            if match:
                logging.info('Попал в match')
                number = int(match.group(1))
                return 'Нет' if 100_000 > number else 'Да'
            if 'Информация по данному источнику отсутствует' == fssp or 'Информация по источнику отсутствует' == fssp:
                return 'Нет'
            elif 'Запрос по источнику не отправлялся' == fssp:
                return '-'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Не удалось получить информацию по арбитражным делам')
            fssp = '-'
        return fssp

    def ind_tax_debts_yes_or_no():
        try:
            tax = ind_tax_debts()
            if '-' == tax or 'Информация по источнику отсутствует' == tax:
                return 'Нет'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Ошибка')
            tax = '-'
            return tax

    def ind_blocked_acc_yes_or_no():
        try:
            blocked = ind_blocked_acc()
            if 'Информация по источнику отсутствует' == blocked or '-' == blocked:
                return 'Нет'
            elif 'Запрос обрабатывается' == blocked:
                return '-'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Ошибка')
            blocked = '-'
            return blocked

    def ind_reestr_np_yes_or_no():
        try:
            rnd = ind_reestr_np()
            if 'Информация не найдена' == rnd or '-' == rnd:
                return 'Нет'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            logging.info('Ошибка')
            rnd = '-'
            return rnd

    def ind_goverment_contracts_yes_or_no():
        try:
            gov = " ".join(
                soup.find('div', class_='card card-nopadding', attrs={'data-element': 'local-state-contracts'}).find(
                    'div', class_='card-section').get_text(' ', strip=True).split())
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return '-'
        logging.info(gov)
        try:
            if 'Информация не найдена' == gov:
                return 'Нет'
            else:
                return 'Да'
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            return 'Нет'

    general_description_of_an_individual = {
        'Паспортные данные:': ind_main_profile('Паспорт:'),
        'Дата рождения:': ind_main_profile('Дата рождения:'),
        'Страна гражданства:': ind_main_profile('Страна гражданства:'),
        'ИНН:': ind_main_profile('ИНН:'),
        'Краткое наименование': ind_fio(),
        'Инфо_ИП': ind_entrepreneur(),
        'Адрес_регистрации': ind_address(),
        'Имя_налог_органа': ind_tax_authority(),
        'История_руководства': ind_is_dir_or_founder_history(),
        'АРБИТРАЖНЫЙ СУД ФЛ': ind_arbit_cases(),
        'АРБИТРАЖНЫЙ СУД ИП/ЮЛ': ind_arbit_cases_ip(),
        'НАЛОГОВАЯ ЗАДОЛЖЕННОСТЬ 2023': ind_tax_debts(),
        'ЗАБЛОКИРОВАННЫЕ РАСЧЕТНЫЕ СЧЕТА (ФЛ)': ind_blocked_acc(),
        'ФЕДЕРАЛЬНАЯ СЛУЖБА СУДЕБНЫХ ПРИСТАВОВ (ФССП ФЛ)': ind_fssp_fl(),
        'РЕЕСТР ЗАЛОГОВ': ind_reestr_zalog(),
        'СООБЩЕНИЯ ФЕДРЕСУРС ФЛ': ind_fed_res(),
        'НАРКОКОНТРОЛЬ (АРХИВ ФСКН)': ind_narcos(),
        'РОСФИНМОНИТОРИНГ: ЭКСТРЕМИСТЫ': ind_ros_fin(),
        'САНКЦИИ США, ЕС, КАНАДЫ': ind_sanc_usa(),
        'ГАС РФ ПРАВОСУДИЕ': ind_justice(),
        'ОСОБЫЕ РЕЕСТРЫ': ind_especially_reestr(),
        'РЕЕСТР НЕДОБРОСОВЕСТНЫХ ПОСТАВЩИКОВ (РНП)': ind_reestr_np(),
        'ФНС - СЕРВИС ПОЛУЧЕНИЯ ИНН': ind_passport(),
        'ДОЛЖНИКИ (ФЛ)': ind_debtor(),
        'Недостоверность сведений (да_нет)': ind_inaccuracy_of_information(),
        'Менее 3 лет (да_нет)': ind_period_of_activity(),
        'Массовый адрес (да_нет)': ind_mass_address(),
        'Сообщения о банкротстве (да_нет)': ind_bankrupt_notices(),
        'Ликвидация (да_нет)': ind_liquid(),
        'Банкротство (да_нет)': ind_bankrupt(),
        'Ответчик (да_нет)': ind_arbitr(),
        'ФССП более 100 (да_нет)': ind_fssp(),
        'Налоговая задолженность (да_нет)': ind_tax_debts_yes_or_no(),
        'Заблокированные счета (да_нет)': ind_blocked_acc_yes_or_no(),
        'РНД (да_нет)': ind_reestr_np_yes_or_no(),
        'Гос контракты (да_нет)': ind_goverment_contracts_yes_or_no()
    }

    return general_description_of_an_individual
