from datetime import datetime as dt

from webapp.config import PATH_FOR_HTML_PAGES, URL_DELTA
from webapp.risk.logger import logging


def download_main_page(driver, client_inn, object_inn, short_name):
    html = driver.page_source
    with open(fr"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f'%d.%m.%Y')}/{object_inn}.html", "w",
              encoding="utf-8") as file:
        file.write(html)


def read_main_page(client_inn, object_inn, short_name):
    with open(f"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f'%d.%m.%Y')}/{object_inn}.html",
              encoding="utf-8") as f:
        html = f.read()
    return html


def download_delta_page(driver, data, client_inn, object_inn, short_name):
    new_url = f"{URL_DELTA}{data['URL_Delta']}"
    driver.execute_script(f"window.open('{new_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    logging.info(f"Переходим на страницу Дельта Аналитики")
    logging.info(f"Current URL: {driver.current_url}")

    html = driver.page_source
    with open(
            f"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f'%d.%m.%Y')}/Delta Аналитика {object_inn}.html",
            "w",
            encoding="utf-8") as file:
        file.write(html)
    driver.implicitly_wait(3)
    driver.close()
    logging.info(f"Возвращаемся обратно на главную страницу компании")
    driver.switch_to.window(driver.window_handles[1])
    logging.info(f"Current URL: {driver.current_url}")


def read_delta_page(client_inn, object_inn, short_name):
    with open(
            f"{PATH_FOR_HTML_PAGES}/{short_name} ИНН {client_inn}/{dt.today().strftime(f'%d.%m.%Y')}/Delta Аналитика {object_inn}.html",
            encoding="utf-8") as f:
        html = f.read()
    return html
