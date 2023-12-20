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

    def check_in_director_base(self, director_inn):
        try:
            db = self.client.managerBase
            return db.directorDetails.find_one({'director_inn': director_inn})
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
                    'client_inn': client_inn,
                    'bank': sheet['G39'].value,
                    'checking_account': sheet['B40'].value,
                    'correspondent_account': sheet['F40'].value,
                    'bik': sheet['I40'].value,
                    'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
                }
                db = self.client.managerBase
                db.companyBankDetails.insert_one(data)
                logging.info(f"Банковские реквизиты клиента ({client_inn}) успешно записаны в MongoDB")
            except Exception as e:
                logging.info("Не записалась информация про банковские реквизиты в MongoDB")
                logging.info(e, exc_info=True)
        else:
            logging.info(f"{client_inn} уже есть в MongoDB")

    def read_mongodb_director_details(self, director_inn):
        try:
            db = self.client.managerBase
            if self.check_in_director_base(director_inn):
                info = {
                    'date_of_birth': db.directorDetails.find_one({'director_inn': director_inn})['date_of_birth'],
                    'place_of_birth': db.directorDetails.find_one({'director_inn': director_inn})['place_of_birth'],
                    'passport': db.directorDetails.find_one({'director_inn': director_inn})['passport'],
                    'issued_by': db.directorDetails.find_one({'director_inn': director_inn})['issued_by'],
                    'department_code': db.directorDetails.find_one({'director_inn': director_inn})[
                        'department_code'],
                    'address_reg': db.directorDetails.find_one({'director_inn': director_inn})['address_reg'],
                    'address_fact': db.directorDetails.find_one({'director_inn': director_inn})['address_fact'],
                }
                return info
            else:
                logging.info(f"{director_inn} отсутствует в MongoDB")
        except Exception as e:
            logging.info("Не прочиталась информация про банковские реквизиты в MongoDB")
            logging.info(e, exc_info=True)
            info = {}
            return info

    def write_to_mongodb_director_details(self, director_inn, sheet):
        if not self.check_in_director_base(director_inn):
            try:
                data = {
                    'director_inn': director_inn,
                    'date_of_birth': sheet['D24'].value,
                    'place_of_birth': sheet['F24'].value,
                    'passport': sheet['D28'].value,
                    'issued_by': sheet['F28'].value,
                    'department_code': sheet['D29'].value,
                    'address_reg': sheet['D30'].value,
                    'address_fact': sheet['E31'].value,
                    'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
                }
                db = self.client.managerBase
                db.directorDetails.insert_one(data)
                logging.info(f"Реквизиты директора ({director_inn}) успешно записаны в MongoDB")
            except Exception as e:
                logging.info("Не записались реквизиты директора в MongoDB")
                logging.info(e, exc_info=True)
        else:
            logging.info(f"Директор ({director_inn}) уже есть в MongoDB")
