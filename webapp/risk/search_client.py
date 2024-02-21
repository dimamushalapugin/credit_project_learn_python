import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from webapp.risk.auth_delta import authorization
from webapp.risk.logger import logging


def update_page(client_inn, driver, person=None):
    driver.implicitly_wait(5)
    if person is not None:
        try:  # нажимает обновить сверху справа
            driver.find_element(By.CSS_SELECTOR, "span[class='more__reload_btn_update']").click()
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
        driver.implicitly_wait(5)

        match len(client_inn):
            case 12:
                try:
                    driver.find_element(By.XPATH, "//div[@class='popup-btn-submit addParams']").click()
                except Exception as _ex:
                    logging.info('Проверяется физ. лицо, но таблица после нажатия "Обновить все" не появилась')
                    logging.info(_ex, exc_info=True)

            case _:
                logging.info('Проверяется юр. лицо')
    else:
        try:  # нажимает обновить сверху справа
            driver.find_element(By.CSS_SELECTOR, "span[class='more__reload_btn_update']").click()
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            driver.find_element(By.XPATH, "//div[@class='popup-btn-submit addParams']").click()

        try:
            driver.find_element(By.XPATH, "//div[@class='popup-btn-submit addParams']").click()
        except Exception as _ex:
            logging.info('Таблица после нажатия "Обновить все" не появилась')

        driver.implicitly_wait(5)

    try:
        driver.find_element(By.XPATH,
                            "//span[@class='cards__column_block-link cards__column_more-link directors_person appear']").click()
    except NoSuchElementException:
        logging.info('Отсутствует раскрыть список')

    try:
        driver.find_element(By.XPATH,
                            "//span[@class='cards__column_block-link cards__column_more-link cards_founders cards_founders_fl appear']").click()
    except NoSuchElementException:
        logging.info('Отсутствует раскрыть список')

    try:
        driver.find_element(By.XPATH,
                            "//span[@class='cards__column_block-link cards__column_more-link directors_history_person appear']").click()
    except NoSuchElementException:
        logging.info('Отсутствует раскрыть список')

    driver.implicitly_wait(2)
    try:
        driver.find_element(By.XPATH,
                            "//span[@class='cards__column_block-link cards__column_more-link founders_person appear']").click()
    except NoSuchElementException:
        logging.info('Отсутствует раскрыть список')

    try:
        driver.find_element(By.XPATH,
                            "//span[@class='cards__column_block-link cards__column_more-link founders_history_person appear']").click()
    except NoSuchElementException:
        logging.info('Отсутствует раскрыть список')

    time.sleep(20)


def search_client(client_inn, caller=None):
    driver = authorization()
    if caller == "create_conclusion":
        logging.info('Обычное риск-заключение')
        try:
            driver.find_element(By.ID, 'autocomplete').send_keys(client_inn)
            driver.implicitly_wait(2)
            driver.find_element(By.CLASS_NAME, 'search-panel__search_submit').click()
            driver.implicitly_wait(5)
            logging.info(f'Стартовая страница: {driver.window_handles}')
            match len(client_inn):
                case 10:
                    driver.find_element(By.CLASS_NAME, 'extra-info-search-link').click()
                case 12:
                    driver.find_element(By.XPATH, "//a[@class='header-nav__link card-title__link']").click()
                case _:
                    logging.info(f'[!] Проверьте корректность ИНН. ИНН: {client_inn}')
                    raise Exception('Проверьте корректность ИНН')
        except Exception as _ex:
            logging.info(_ex, exc_info=True)
            raise _ex
        driver.switch_to.window(driver.window_handles[1])
    else:
        logging.info('Проверка физ. лица')
        try:
            new_url = f"https://sb.deltasecurity.ru/search/person?text={client_inn}&user_text="
            driver.execute_script(f"window.open('{new_url}', '_self');")
            driver.implicitly_wait(2)
            driver.find_element(By.XPATH, "//a[@class='header-nav__link card-title__link']").click()
        except Exception:
            logging.info('Таких людей нет в базе данных Дельты')
            new_url = f"https://sb.deltasecurity.ru/contractor/new-person/?text={client_inn}"
            driver.execute_script(f"window.open('{new_url}', '_self');")

    logging.info(driver.window_handles)
    logging.info("Переход на страницу лизингополучателя")
    logging.info(f"Current URL: {driver.current_url}")

    return driver
