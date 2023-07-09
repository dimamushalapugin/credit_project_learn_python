import requests


def parsing_egrul_json(company_inn):
    url = f'https://egrul.itsoft.ru/{company_inn}.json'
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.json()
    except(requests.RequestException, ValueError):
        return {}


def get_customer_name(request_form):
    info_about_customer = parsing_egrul_json(request_form)
    if 'СвЮЛ' in info_about_customer:
        try:
            info_about_customer = info_about_customer['СвЮЛ']['СвНаимЮЛ']['СвНаимЮЛСокр']['@attributes'][
                'НаимСокр'].upper()
        except KeyError:
            info_about_customer = None
    elif 'СвИП' in info_about_customer:
        info_about_customer = info_about_customer.get('СвИП')
        if info_about_customer:
            fio_rus = info_about_customer.get('СвФЛ', {}).get('ФИОРус', {}).get('@attributes', {})
            first_name = fio_rus.get('Имя', '-').upper()
            last_name = fio_rus.get('Фамилия', '-').upper()
            patronymic = fio_rus.get('Отчество', '-').upper()
            info_about_customer = f'{last_name} {first_name} {patronymic}'
        else:
            info_about_customer = None
    else:
        info_about_customer = None

    return info_about_customer
