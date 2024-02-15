import requests
from webapp.risk.logger import logging
from webapp.config import FAST_API_URL


def process_excel(temp_path, finish_path):
    # Открываем файл и отправляем его на сервер Windows
    with open(temp_path, 'rb') as file:
        files = {'file': file}
        logging.info(f'Путь к отправляемому файлу: {temp_path}')
        logging.info('Отправляем файл на сервер Windows...')
        response = requests.post(FAST_API_URL, files=files)

    # Проверяем ответ сервера
    if response.status_code == 200:
        # Файл был успешно обработан, сохраняем его на сервере Linux
        logging.info(f'Путь к обработанному файлу: {finish_path}')
        if finish_path.exists():
            logging.info('Файл уже существует, его надо удалить')
            finish_path.unlink()
            logging.info('Файл удален')
        with open(finish_path, 'wb') as f:
            logging.info('Сохраняем файл...')
            f.write(response.content)
        logging.info('Файл успешно обработан и сохранен')
    else:
        # Произошла ошибка при отправке файла на сервер Windows
        error_msg = f'Ошибка {response.status_code}: {response.text}'
        logging.error(error_msg)
        logging.info('Произошла ошибка при обработке файла')
