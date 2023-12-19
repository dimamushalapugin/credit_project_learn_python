from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime

from webapp.config import MONGO_URL
from webapp.risk.logger import logging


def write_to_mongodb_risk_count(curr_user, client_inn, seller_inn):
    data = {
        'user': str(curr_user).split()[-1],
        'time': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
        'client': client_inn,
        'seller': seller_inn
    }
    client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        logging.info("Pinged your deployment. You successfully connected to MongoDB!")
        db = client.riskBase
        db.countRiskConclusions.insert_one(data)
    except Exception as e:
        logging.info("Не записалась информация в MongoDB")
        logging.info(e, exc_info=True)


def write_to_mongodb_app_count(curr_user, client_inn, seller_inn1, seller_inn2, seller_inn3, seller_inn4):
    data = {
        'user': str(curr_user).split()[-1],
        'time': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
        'client': client_inn,
        'sellers': {
            'inn1': seller_inn1,
            'inn2': seller_inn2,
            'inn3': seller_inn3,
            'inn4': seller_inn4
        }
    }
    client = MongoClient(MONGO_URL)
    try:
        db = client.managerBase
        db.countManagerApps.insert_one(data)
    except Exception as e:
        logging.info("Не записалась информация в MongoDB")
        logging.info(e, exc_info=True)
