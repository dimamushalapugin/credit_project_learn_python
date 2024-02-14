import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from webapp.config import LOGIN_DELTA, PASSWORD_DELTA, URL_DELTA
from webapp.risk.logger import logging


def authorization():
    options = Options()
    options.add_argument("--headless")
    logging.info(f'Создаем драйвер Selenium')
    service = webdriver.FirefoxService(log_output=subprocess.STDOUT)
    driver = webdriver.Firefox(options=options, service=service)
    try:
        driver.get(URL_DELTA)
        driver.maximize_window()
        driver.implicitly_wait(3)
        driver.find_element(By.NAME, 'user[login]').send_keys(LOGIN_DELTA)
        driver.find_element(By.NAME, 'user[password]').send_keys(PASSWORD_DELTA)
        driver.find_element(By.XPATH, "//input[@value='Войти']").click()
        driver.implicitly_wait(2)

        if len(driver.find_elements(By.XPATH, '//div[@class="popup-btn-submit force-login"]')) > 0:
            driver.find_element(By.XPATH, '//div[@class="popup-btn-submit force-login"]').click()

        logging.info(f'Авторизация прошла успешно')
    except Exception as _ex:
        logging.info(f'Ошибка авторизации')
        logging.info(_ex, exc_info=True)

    return driver
