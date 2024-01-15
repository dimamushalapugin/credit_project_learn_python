# import os

# from datetime import datetime as dt
# from typing import Optional
# from docx import Document
# from num2words import num2words
# from flask_login import current_user
# from webapp.config import DADATA_BASE
# from webapp.risk.logger import logging
# from webapp.risk.mongo_db import MongoDB
from retrying import retry
import httpx
from dadata import Dadata

DADATA_TOKEN = "804d29658b186056c6cfab57f94c68695581d747"
DADATA_SECRET = "2c54bab544f947c975525ab452d014492122e52b"
DADATA_BASE = Dadata(DADATA_TOKEN, DADATA_SECRET)


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def main_result_dadata(someone):
    try:
        main_result = DADATA_BASE.find_by_id("party", someone)
        print(main_result)
        return main_result
    except httpx.ConnectTimeout:
        print("Timeout error occurred. Retrying...")
        raise


# def main_result_dadata(someone):
#     main_result = DADATA_BASE.find_by_id("party", someone)
#     print(main_result)
#     return main_result
# main_result_dadata('1655099271')

def naming_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        full_name_bki_ur = main_result[0]['data']['name']['full_with_opf']
    except:
        full_name_bki_ur = ''
    print(full_name_bki_ur)
    return full_name_bki_ur


# naming_dadata_bk_ur('1655099271')

def ogrn_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        ogrn_bki_ur = main_result[0]['data']['ogrn']
    except:
        ogrn_bki_ur = ''
    print(ogrn_bki_ur)
    return ogrn_bki_ur


# ogrn_dadata_bk_ur('1655099271')

def address_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    try:
        address_bki_ur = main_result[0]['data']['address']['unrestricted_value']
    except:
        address_bki_ur = ''
    print(address_bki_ur)
    return address_bki_ur


# address_dadata_bk_ur('1427010997')

def fio_dadata_bk_ur(someone):
    main_result = main_result_dadata(someone)
    ip_or_kfh = 'Нет'
    try:
        if main_result[0]['data']['opf']['short'] in ['ИП']:
            ip_or_kfh = 'Да'
        if ip_or_kfh == 'Нет':
            fio_bki_ur = main_result[0]['data']['management']['name']
        else:
            fio_bki_ur = main_result[0]['data']['name']['full']
    except:
        fio_bki_ur = ''
    print(fio_bki_ur)
    return fio_bki_ur


# fio_dadata_bk_ur('6120001800')

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
    print(leader_bki_ur)
    return leader_bki_ur


# leader_dadata_bk_ur('771386745859')

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
    print(doverka_ustav_bki_ur)
    return doverka_ustav_bki_ur
# doverka_ustav_dadata_bk_ur('1655099271')
