import requests

from cachetools import TTLCache
from webapp.config import CHECKO_URL
from webapp.risk.logger import logging


class FindInd:
    """
    Класс для поиска информации по ИНН с возможностью кеширования.
    """

    __url = CHECKO_URL

    def __init__(self, inn):
        """
        Инициализация объекта класса FindInd.

        :param inn: ИНН (Идентификационный номер налогоплательщика).
        """
        self.__inn = inn
        self.cache = TTLCache(maxsize=128, ttl=172800)  # TTL в секундах (2 дня)

    @property
    def info(self):
        """
        Получение информации по ИНН, используя кеш при наличии.

        :return: Информация в формате JSON или None, если запрос неудачен.
        """
        if self.__inn in self.cache:
            return self.cache[self.__inn]
        result = self._get_info()
        self.cache[self.__inn] = result
        return result

    def _get_info(self):
        """
        Внутренний метод для выполнения запроса и получения информации по ИНН.

        :return: Информация в формате JSON или None, если запрос неудачен.
        """
        try:
            response = requests.get(f'{self.__url}inn={self.__inn}')
            response.raise_for_status()
            json_data = response.json()
            return json_data
        except requests.exceptions.RequestException as e:
            logging.info(f"Error during request: {e}")
            return None

    @property
    def get_fio(self):
        """
        Получение ФИО физического лица из информации, полученной по ИНН.

        :return: ФИО физического лица или пустая строка, если информация отсутствует.
        """
        if self.info:
            return self.info.get('data', {}).get('ФИО', '')
        logging.info("Не нашел ФИО физ. лица")
        return ''
