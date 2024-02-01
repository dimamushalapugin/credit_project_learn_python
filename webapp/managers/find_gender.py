from webapp.config import DADATA_BKI
from webapp.risk.logger import logging


class Gender:
    def __init__(self, name):
        self.__name = name
        self.__data = self.__genus(name)

    def __repr__(self):
        return f"{self.__name}, пол: {self.__get_gender}, имя в род. падеже: {self.get_name}"

    @staticmethod
    def __genus(name):
        try:
            return DADATA_BKI.clean("name", name)
        except Exception as e:
            logging.info(e, exc_info=True)
            return name

    @property
    def __get_gender(self):
        return self.__data.get("gender")

    @property
    def get_name(self):
        return self.__data.get("result_genitive")
