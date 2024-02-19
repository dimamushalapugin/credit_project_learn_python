import json
from datetime import datetime


class DescriptionOfLessee:
    """
    Класс для описания лизингополучателя.

    Attributes:
        self.data (str): JSON-строка с информацией о лизингополучателе.
    """

    def __init__(self, data):
        if not data:
            data = '{}'  # Пустой объект JSON, если data равен None
        self.info = json.loads(data)

    @property
    def get_name(self):
        return self.info.get('value', '').upper()

    @property
    def get_inn(self):
        return self.info.get('data').get('inn')

    @property
    def get_ogrn(self):
        return self.info.get('data').get('ogrn')

    @property
    def get_registration_address(self):
        return self.info.get('data').get('address').get('value')

    @property
    def get_registration_date(self):
        # Преобразование в дату
        normal_date = datetime.fromtimestamp(self.info.get('data').get('ogrn_date') / 1000.0)
        formatted_date = normal_date.strftime('%d.%m.%Y')
        return formatted_date

    def __repr__(self):
        return f'{self.get_name} ИНН: {self.get_inn}'
