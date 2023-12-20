from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime

from webapp.config import MONGO_URL
from webapp.risk.logger import logging


class MongoDB:
    def __init__(self, current_user):
        self.client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
        self.curr_user = current_user

    def write_to_mongodb_risk_count(self, client_inn, seller_inn):
        data = {
            'user': str(self.curr_user).split()[-1],
            'time': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
            'client': client_inn,
            'seller': seller_inn
        }
        try:
            self.client.admin.command('ping')
            logging.info("Pinged your deployment. You successfully connected to MongoDB!")
            db = self.client.riskBase
            db.countRiskConclusions.insert_one(data)
        except Exception as e:
            logging.info("Не записалась информация в MongoDB")
            logging.info(e, exc_info=True)

    def write_to_mongodb_app_count(self, client_inn, seller_inn1, seller_inn2, seller_inn3, seller_inn4):
        data = {
            'user': str(self.curr_user).split()[-1],
            'time': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
            'client': client_inn,
            'sellers': {
                'inn1': seller_inn1,
                'inn2': seller_inn2,
                'inn3': seller_inn3,
                'inn4': seller_inn4
            }
        }
        try:
            db = self.client.managerBase
            db.countManagerApps.insert_one(data)
        except Exception as e:
            logging.info("Не записалась информация в MongoDB")
            logging.info(e, exc_info=True)

    def check_in_manager_base(self, client_inn):
        try:
            db = self.client.managerBase
            return db.companyBankDetails.find_one({'client_inn': client_inn})
        except Exception as e:
            logging.info("Не прочиталась информация в MongoDB")
            logging.info(e, exc_info=True)
            return False

    def read_mongodb_bank_details(self, client_inn):
        try:
            db = self.client.managerBase
            if self.check_in_manager_base(client_inn):
                info = {
                    'bank': db.companyBankDetails.find_one({'client_inn': client_inn})['bank'],
                    'check_account': db.companyBankDetails.find_one({'client_inn': client_inn})['checking_account'],
                    'cor_account': db.companyBankDetails.find_one({'client_inn': client_inn})['correspondent_account'],
                    'bik': db.companyBankDetails.find_one({'client_inn': client_inn})['bik'],
                }
                return info
            else:
                logging.info(f"{client_inn} отсутствует в MongoDB")
        except Exception as e:
            logging.info("Не прочиталась информация про банковские реквизиты в MongoDB")
            logging.info(e, exc_info=True)
            info = {}
            return info

    def write_to_mongodb_bank_details(self, client_inn, sheet):
        if not self.check_in_manager_base(client_inn):
            try:
                data = {
                    'bank': sheet['G39'].value,
                    'checking_account': sheet['B40'].value,
                    'correspondent_account': sheet['F40'].value,
                    'bik': sheet['I40'].value,
                }
                db = self.client.managerBase
                db.companyBankDetails.insert_one(data)
            except Exception as e:
                logging.info("Не записалась информация про банковские реквизиты в MongoDB")
                logging.info(e, exc_info=True)
        else:
            logging.info(f"{client_inn} уже есть в MongoDB")
