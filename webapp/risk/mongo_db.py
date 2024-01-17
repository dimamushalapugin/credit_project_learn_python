from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime

from webapp.config import MONGO_URL
from webapp.risk.logger import logging
from webapp.risk.xlsx_models import XlsxCreator


class MongoDB:
    def __init__(self, current_user):
        try:
            self.client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
        except Exception as e:
            logging.info(e, exc_info=True)
            try:
                self.client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
            except Exception as e:
                logging.info('Второй раз тоже не подключился к MongoDB')
                logging.info(e, exc_info=True)

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
                    'phone': db.companyBankDetails.find_one({'client_inn': client_inn})['phone'],
                    'email': db.companyBankDetails.find_one({'client_inn': client_inn})['email'],
                }
                return info
            else:
                logging.info(f"Лизингополучатель (ИНН: {client_inn}) отсутствует в MongoDB")
        except Exception as e:
            logging.info("Не прочиталась информация про банковские реквизиты в MongoDB")
            logging.info(e, exc_info=True)
            info = {}
            return info

    @staticmethod
    def __set_details(db, data, mongo_key, cell, inn, key_inn, xlsx):
        if data.get(mongo_key) != xlsx.get_cell(cell) and not xlsx.is_cell_none(cell):
            logging.info(f'{data.get(mongo_key)} -> {xlsx.get_cell(cell)}')
            data[mongo_key] = xlsx.get_cell(cell)
            db.update_one({key_inn: inn}, {'$set': {
                mongo_key: xlsx.get_cell(cell)
            }})

    def __update_mongodb_bank_details(self, db, inn, xlsx, key_inn):
        try:
            data = db.find_one({key_inn: inn})
        except Exception as e:
            logging.info(e, exc_info=True)
            data = {}

        logging.info('UPDATE MONGODB BANK DETAILS')
        logging.info('=' * 40)
        try:
            self.__set_details(db, data, 'bank', 'G40', inn, key_inn, xlsx)
            self.__set_details(db, data, 'check_account', 'B41', inn, key_inn, xlsx)
            self.__set_details(db, data, 'cor_account', 'F41', inn, key_inn, xlsx)
            self.__set_details(db, data, 'bik', 'I41', inn, key_inn, xlsx)
            self.__set_details(db, data, 'phone', 'C21', inn, key_inn, xlsx)
            self.__set_details(db, data, 'email', 'F21', inn, key_inn, xlsx)
        except Exception as e:
            logging.info(e, exc_info=True)
            logging.info('Не удалось обновить банковские реквизиты')

        logging.info('=' * 40)

    def write_to_mongodb_bank_details(self, client_inn, sheet):
        xlsx = XlsxCreator(sheet)
        data = {
            'client_inn': client_inn,
            'bank': xlsx.get_cell('G40'),
            'checking_account': xlsx.get_cell('B41'),
            'correspondent_account': xlsx.get_cell('F41'),
            'bik': xlsx.get_cell('I41'),
            'phone': xlsx.get_cell('C21'),
            'email': xlsx.get_cell('F21'),
            'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S"),
        }
        if not self.check_in_manager_base(client_inn):
            try:
                db = self.client.managerBase.companyBankDetails
                db.insert_one(data)
                logging.info(f"Банковские реквизиты клиента ({client_inn}) успешно записаны в MongoDB")
            except Exception as e:
                logging.info("Не записалась информация про банковские реквизиты в MongoDB")
                logging.info(e, exc_info=True)
        else:
            logging.info(f"Лизингополучатель (ИНН: {client_inn}) уже есть в MongoDB")
            try:
                db = self.client.managerBase.companyBankDetails
                self.__update_mongodb_bank_details(db, client_inn, xlsx, 'client_inn')
            except Exception as e:
                logging.info(e, exc_info=True)

    def read_mongodb_director_details(self, director_inn):
        try:
            db = self.client.managerBase
            if self.check_in_director_base(director_inn):
                info = {
                    'director_name': db.directorDetails.find_one({'director_inn': director_inn})['director_name'],
                    'date_of_birth': db.directorDetails.find_one({'director_inn': director_inn})['date_of_birth'],
                    'place_of_birth': db.directorDetails.find_one({'director_inn': director_inn})['place_of_birth'],
                    'passport_series': db.directorDetails.find_one({'director_inn': director_inn})['passport_series'],
                    'passport_id': db.directorDetails.find_one({'director_inn': director_inn})['passport_id'],
                    'issued_by': db.directorDetails.find_one({'director_inn': director_inn})['issued_by'],
                    'issued_when': db.directorDetails.find_one({'director_inn': director_inn})['issued_when'],
                    'department_code': db.directorDetails.find_one({'director_inn': director_inn})[
                        'department_code'],
                    'address_reg': db.directorDetails.find_one({'director_inn': director_inn})['address_reg'],
                    'address_fact': db.directorDetails.find_one({'director_inn': director_inn})['address_fact'],
                }
                return info
            else:
                logging.info(f"Директор (ИНН: {director_inn}) отсутствует в MongoDB")
        except Exception as e:
            logging.info("Не прочиталась информация про банковские реквизиты в MongoDB")
            logging.info(e, exc_info=True)
            info = {}
            return info

    def __update_mongodb_director_details(self, db, inn, xlsx, key_inn):
        try:
            data = db.find_one({key_inn: inn})
        except Exception as e:
            logging.info(e, exc_info=True)
            data = {}

        logging.info('UPDATE MONGODB DIRECTOR DETAILS')
        logging.info('=' * 40)
        try:
            self.__set_details(db, data, 'director_name', 'C23', inn, key_inn, xlsx)
            self.__set_details(db, data, 'date_of_birth', 'D24', inn, key_inn, xlsx)
            self.__set_details(db, data, 'place_of_birth', 'F24', inn, key_inn, xlsx)
            self.__set_details(db, data, 'passport_series', 'D28', inn, key_inn, xlsx)
            self.__set_details(db, data, 'passport_id', 'D29', inn, key_inn, xlsx)
            self.__set_details(db, data, 'issued_by', 'F28', inn, key_inn, xlsx)
            self.__set_details(db, data, 'issued_when', 'F29', inn, key_inn, xlsx)
            self.__set_details(db, data, 'department_code', 'D30', inn, key_inn, xlsx)
            self.__set_details(db, data, 'address_reg', 'D31', inn, key_inn, xlsx)
            self.__set_details(db, data, 'address_fact', 'E32', inn, key_inn, xlsx)
        except Exception as e:
            logging.info(e, exc_info=True)
            logging.info('Не удалось обновить реквизиты директора')
        logging.info('=' * 40)

    def write_to_mongodb_director_details(self, director_inn, sheet):
        xlsx = XlsxCreator(sheet)
        data = {
            'director_name': xlsx.get_cell('C23'),
            'director_inn': director_inn,
            'date_of_birth': xlsx.get_cell('D24'),
            'place_of_birth': xlsx.get_cell('F24'),
            'passport_id': xlsx.get_cell('D29'),
            'passport_series': xlsx.get_cell('D28'),
            'issued_by': xlsx.get_cell('F28'),
            'issued_when': xlsx.get_cell('F29'),
            'department_code': xlsx.get_cell('D30'),
            'address_reg': xlsx.get_cell('D31'),
            'address_fact': xlsx.get_cell('E32'),
            'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
        }
        if not self.check_in_director_base(director_inn):
            try:
                db = self.client.managerBase.directorDetails
                db.insert_one(data)
                logging.info(f"Реквизиты директора ({director_inn}) успешно записаны в MongoDB")
            except Exception as e:
                logging.info("Не записались реквизиты директора в MongoDB")
                logging.info(e, exc_info=True)
        else:
            logging.info(f"Директор ({director_inn}) уже есть в MongoDB")
            try:
                db = self.client.managerBase.directorDetails
                self.__update_mongodb_director_details(db, director_inn, xlsx, 'director_inn')
            except Exception as e:
                logging.info(e, exc_info=True)
