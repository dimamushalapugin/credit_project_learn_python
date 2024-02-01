import datetime
import httpx

from retrying import retry
from webapp.config import DADATA_BASE
from webapp.risk.logger import logging


class SaveCache:
    result = {}

    def __init__(self, inn):
        self.inn = inn

    @property
    def check(self):
        return self.inn in self.result and self.result[self.inn]['date'] == datetime.date.today()

    def save(self, result):
        self.result[self.inn] = {'result': result, 'date': datetime.date.today()}

    @property
    def get_result(self):
        return self.result[self.inn]['result']

    def __repr__(self):
        return f'Сейчас в кеше: {self.result}'

    @property
    def size(self):
        return f'Размер кеша: {self.result.__sizeof__()} байт. Кол-во компаний: {len(self.result)}'


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def main_result_dadata(someone):
    inn = SaveCache(someone)
    try:
        if inn.check:
            return inn.get_result
        else:
            main_result = DADATA_BASE.find_by_id("party", someone)
            inn.save(main_result)
            logging.info(inn.size)
            return main_result
    except httpx.ConnectTimeout:
        logging.info("Timeout error occurred. Retrying...")
        raise


def naming_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        full_name_bki_ur = main_result[0]['data']['name']['full_with_opf']
    except:
        full_name_bki_ur = ''
    return full_name_bki_ur


def ogrn_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        ogrn_bki_ur = main_result[0]['data']['ogrn']
    except:
        ogrn_bki_ur = ''
    return ogrn_bki_ur


def address_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        address_bki_ur = main_result[0]['data']['address']['unrestricted_value']
    except:
        address_bki_ur = ''
    return address_bki_ur


def fio_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    ip_or_kfh = 'Нет'
    try:
        if main_result[0]['data']['opf']['short'] in ['ИП', 'ГКФХ']:
            ip_or_kfh = 'Да'
        if ip_or_kfh == 'Нет':
            fio_bki_ur = main_result[0]['data']['management']['name']
        else:
            fio_bki_ur = main_result[0]['data']['name']['full']
    except:
        fio_bki_ur = ''
    return fio_bki_ur


def leader_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    ip_or_kfh = 'Нет'
    try:
        if main_result[0]['data']['opf']['short'] in ['ИП']:
            ip_or_kfh = 'Да'
        if ip_or_kfh == 'Нет':
            leader_bki_ur = main_result[0]['data']['management']['post']
        else:
            leader_bki_ur = main_result[0]['data']['opf']['full']
    except:
        leader_bki_ur = ''
    return leader_bki_ur


def doverka_ustav_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    ip_or_kfh = 'Нет'
    try:
        if main_result[0]['data']['opf']['short'] in ['ИП', 'КФХ', 'ГКФХ']:
            ip_or_kfh = 'Да'
        if ip_or_kfh == 'Нет':
            doverka_ustav_bki_ur = 'Устава'
        else:
            doverka_ustav_bki_ur = 'Свидетельства о регистрации индивидуального предпринимателя'
    except:
        doverka_ustav_bki_ur = ''
    return doverka_ustav_bki_ur
