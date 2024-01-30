import pytest
import requests

from unittest.mock import patch
from webapp.managers.indiv_bki import FindInd


@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get


def test__get_info_success(mock_requests_get):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = {'data': {'ИНН': '123456789', 'ФИО': 'Тестовый Пользователь'}}

    finder = FindInd('123456789')
    result = finder._get_info()

    assert result == {'data': {'ИНН': '123456789', 'ФИО': 'Тестовый Пользователь'}}


def test__get_info_failure(mock_requests_get):
    mock_requests_get.side_effect = requests.exceptions.RequestException('Mocked error')

    finder = FindInd('987654321')
    result = finder._get_info()

    assert result is None
