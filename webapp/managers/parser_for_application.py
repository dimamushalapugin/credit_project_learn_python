import openpyxl
import docx
import os
import datetime

from docx import Document
from dadata import Dadata
from docx.shared import Pt
from datetime import datetime as dt
from selenium.webdriver.edge.options import Options
from flask_login import current_user
from webapp.risk.logger import logging
from webapp.managers.parser_for_dkp import read_xlsx
from num2words import num2words
from webapp.config import DADATA_TOKEN, DADATA_SECRET, DADATA_BASE
from selenium import webdriver
from selenium.webdriver.common.by import By


def start_filling_application(inn_leasee, path_application, inn_seller1, inn_seller2, inn_seller3, inn_seller4):
    logging.info(f"({current_user}) Этап 1.")
    temporary_path = r'webapp\static\temporary'
    path_for_download = r'static\temporary'
    ip_or_kfh = 'Нет'
    type_business = ''
    full_krakt_name_leasee = ''
    main_activity_leasee = ''
    ogrn_leasee = ''
    okpo_leasee = ''
    okato_leasee = ''
    date_regist = ''
    ustav_capital = ''
    inn_kpp_leasee = ''
    address_leasee = ''
    formatted_name_leader_leasee = ''
    fio_list = ''
    inn_list = ''
    dolya_list = ''
    full_name_leasee = ''
    leader_leasee = ''
    fio_leader = ''
    phone_leasee = ''
    email_leasee = ''
    krakt_name_seller1 = ''
    krakt_name_seller2 = ''
    krakt_name_seller3 = ''
    krakt_name_seller4 = ''
    address_seller1 = ''
    address_seller2 = ''
    address_seller3 = ''
    address_seller4 = ''
    inn_dir_leasee = ''

    def parser_info_leasee(inn_leasee):
        logging.info(f"({current_user}) Этап 2.")
        nonlocal ip_or_kfh, type_business, inn_dir_leasee, krakt_name_seller1, address_seller1, krakt_name_seller2, address_seller2, krakt_name_seller3, address_seller3, krakt_name_seller4, address_seller4, full_krakt_name_leasee, main_activity_leasee, ogrn_leasee, okpo_leasee, okato_leasee, date_regist, ustav_capital, inn_kpp_leasee, address_leasee, formatted_name_leader_leasee, fio_list, inn_list, dolya_list, full_name_leasee, leader_leasee, fio_leader, phone_leasee, email_leasee

        logging.info(f"({inn_leasee})")

        dadata = Dadata(DADATA_TOKEN)
        result = dadata.find_by_id("party", inn_leasee)
        logging.info(f"{result}")

        ip_or_kfh = 'Нет'
        if result[0]['data']['opf']['short'] in ['ИП', 'КФХ', 'ГКФХ']:
            ip_or_kfh = 'Да'

        full_name_leasee = result[0]['data']['name']['full_with_opf']

        full_krakt_name_leasee = result[0]['data']['name']['short_with_opf']

        if ip_or_kfh == 'Нет':
            inn_kpp_leasee = inn_leasee + '/' + result[0]['data']['kpp']
            leader_leasee = result[0]['data']['management']['post']
            fio_leader = result[0]['data']['management']['name']
        else:
            inn_kpp_leasee = inn_leasee
            type_business = result[0]['data']['opf']['short']
            leader_leasee = result[0]['data']['opf']['short']
            if result[0]['data']['opf']['short'] == 'ИП':
                leader_leasee = 'Индивидуальный предприниматель'
            else:
                leader_leasee = 'Глава'
            fio_leader = result[0]['data']['name']['full']

        last_name, first_name, patronymic_name = fio_leader.split()

        # Get the initial of the first name
        first_name_initial = first_name[0]

        # Get the initial of the patronymic name
        patronymic_initial = patronymic_name[0]

        # Combine the last name and initials in the desired format
        formatted_name_leader_leasee = f'{last_name} {first_name_initial}.{patronymic_initial}.'

        address_leasee = result[0]['data']['address']['unrestricted_value']

        ogrn_leasee = result[0]['data']['ogrn']

        okato_leasee = result[0]['data']['okato']

        okpo_leasee = result[0]['data']['okpo']

        # Значение registration_date в миллисекундах
        registration_date_ms = result[0]['data']['ogrn_date']
        # Преобразуем значение в объект datetime
        registration_date = datetime.datetime.fromtimestamp(registration_date_ms / 1000)
        # Преобразование строки в объект datetime
        date_time_obj = datetime.datetime.strptime(str(registration_date), "%Y-%m-%d %H:%M:%S")
        # Форматирование даты в нужный формат
        date_regist = date_time_obj.strftime("%d.%m.%Y")

        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Edge(options=options)
        driver.get(f"https://vbankcenter.ru/contragent/{ogrn_leasee}")
        full_info_leasee_vbc = driver.find_element(By.XPATH, "/html/body").text.split('\n')
        # full_info_leasee_vbc = ['ВСЕРОССИЙСКИЙ', 'БИЗНЕС ЦЕНТР', 'Госзакупки', 'TenChat', 'Маркетплейс', 'Агентам', 'Партнерам', 'О проекте', '8 (800) 300-43-43', 'обратный звонок', 'ВОЙТИ', 'Бизнес России', 'Соцсеть для заработка', 'Торги по банкротству', 'Субподряды', 'Маркет', 'ООО "ИНВЕСТСТРОЙПРОЕКТ"', 'ДЕЙСТВУЕТ', 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ИНВЕСТСТРОЙПРОЕКТ"', 'Учредители', 'Сотрудники', 'Связи', 'Контакты', 'Финансы', 'Правовая среда', 'О компании', 'Репутация компании', '5.0', 'Все отзывы', '2', 'Отзывы клиентов', '2', 'Отзывы сотрудников', '0', 'Отзывы партнеров', '0', 'Связаться с компанией', 'Задать вопрос', 'Уставный капитал, ₽', '11 тыс', 'Баланс, ₽', '449,76 млн (2022 г.)', '+66,71 млн (17,42%)', 'Чистая прибыль, ₽', '8,8 млн (2022 г.)', '-315 тыс (-3,45%)', 'Выручка, ₽', '707,31 млн (2022 г.)', '+299,68 млн (73,52%)', 'Налоги, ₽', '13,6 млн (2021 г.)', '-1,7 млн (-11,09%)', 'Взносы, ₽', '2,56 млн (2021 г.)', '-1,41 млн (-35,57%)', 'Основные реквизиты', 'Дата создания: ', '20.02.2016', 'ИНН: ', '1657220036', 'КПП: ', '165701001', 'ОГРН: ', '1161690070134', 'Все реквизиты (ФНС / ПФР / ФСС)', 'Банковские счета', 'Руководитель', 'Директор:', 'Валиев Ильнур Исламович', 'с 02.09.2021', 'ИНН: 162200912337', 'Все руководители', 'Юридический адрес', '420133, РЕСПУБЛИКА ТАТАРСТАН, Г. КАЗАНЬ, УЛ. АКАДЕМИКА ЛАВРЕНТЬЕВА, Д. 11, ПОМЕЩ. 1045', 'Контакты', 'Телефон: ', '+7 (843) 216-06-19', 'E-mail: ', 'isp555@mail.ru', 'Показать еще (2)', 'Количество сотрудников', '25 сотрудников (2022)', '30 сотрудников (2021)', 'Показать еще (4)', 'Средняя зарплата', '62 381 рубля (2021)', '81 477 рублей (2020)', 'Показать еще (3)', 'Реестр МСП', 'Малое предприятие', 'с 01.08.2016', 'Налоговый орган', 'МЕЖРАЙОННАЯ ИНСПЕКЦИЯ ФЕДЕРАЛЬНОЙ НАЛОГОВОЙ СЛУЖБЫ № 5 ПО РЕСПУБЛИКЕ ТАТАРСТАН', 'с 20.02.2016', 'Основной вид деятельности', 'Строительство жилых и нежилых зданий (41.20) Все виды деятельности (15)', 'Сведения Росстата', 'ОКПО: ', '00050587', 'Показать еще (4)', 'Отчет в PDF', 'Выписка из ЕГРЮЛ', 'Следить за организацией', 'Поделиться', '89', 'баллов', 'Надёжная компания', 'Расскажите о надёжности компании', 'своим партнерам и клиентам', 'Разместить на сайте', 'Индекс финансового доверия', 'Оцените лимит аванса с компанией', 'Вероятность риска', '3 %', 'Сумма аванса', '318,6 млн ₽', 'Безопасная сумма аванса 318,6 млн ₽', '10 000 ₽', '1,03 млрд ₽', 'Актуально на 20.08.2023', 'ООО "ИНВЕСТСТРОЙПРОЕКТ" ИНН 1657220036 ОГРН 1161690070134 создано 20.02.2016 по юридическому адресу 420133, РЕСПУБЛИКА ТАТАРСТАН, Г. КАЗАНЬ, УЛ. АКАДЕМИКА ЛАВРЕНТЬЕВА, Д. 11, ПОМЕЩ. 1045. Статус организации: действует. Информация о руководителе: Валиев Ильнур Исламович. Уставный капитал организации: 11000. В выписке из официального реестра ЕГРЮЛ в лице учредителей отражено 1 российское юридическое лицо Основной вид деятельности - Строительство жилых и нежилых зданий. Организация присутствует в реестре МСП как Малое 01.08.2016 состоит на учете в налоговом органе МЕЖРАЙОННАЯ ИНСПЕКЦИЯ ФЕДЕРАЛЬНОЙ НАЛОГОВОЙ СЛУЖБЫ № 5 ПО РЕСПУБЛИКЕ ТАТАРСТАН с 20.02.2016. Регистрационный номер в ПФР - 013504034917, в ФСС - 160500031316051', 'Подробнее', 'Искали другую одноименную компанию? Можете посмотреть все организации с названием ООО "ИНВЕСТСТРОЙПРОЕКТ"', 'Финансы', 'Данные по финансовым показателям приведены на основании бухгалтерской отчетности за 2012–2020 годы', 'Выручка', '707,31 млн +299,68 млн', '2022 г.', 'Прибыль', '8,8 млн -315 тыс', '2022 г.', 'Налоги', '13,6 млн -1,7 млн', '2021 г.', '800', '400', '0', '2016', '2017', '2018', '2019', '2020', '2021', '2022', 'млн., ₽', 'Госконтракты', 'Организация ООО "ИНВЕСТСТРОЙПРОЕКТ" выступила поставщиком в 60 госконтрактах на сумму 5,5 млрд ₽', 'Поставщик (60)', 'Заказчик (0)', 'ФКУ УПРДОР "ПРИКАМЬЕ"', '41 контракт на сумму  2 911 153 496 ₽', 'ФКУ "ВОЛГО-ВЯТСКУПРАВТОДОР"', '12 контрактов на сумму  1 194 645 467 ₽', 'ФКУ УПРДОР "ЮЖНЫЙ УРАЛ"', '6 контрактов на сумму  1 377 903 503 ₽', 'ФКУ УПРДОР МОСКВА - НИЖНИЙ НОВГОРОД', '1 контракт на сумму  11 950 000 ₽', 'Компания зарегистрирована в едином реестре участников закупок под номером №19032618 от 02.11.2021', 'РНП', 'По данным ФАС организация не внесена в реестр недобросовестных поставщиков.', 'Проверки', 'За весь период в отношении ООО "ИНВЕСТСТРОЙПРОЕКТ" проведено 4 проверки', 'Плановые', '0', 'Внеплановые', '4', 'Нарушений', '4', 'Предстоит проверок', '0', 'Все проверки', 'Исполнительные производства', 'В отношении организации ООО "ИНВЕСТСТРОЙПРОЕКТ" выявлено 1 открытое производство', 'Открытых производств', 'На сумму, ₽', '1', '300 000', 'Иное', '1', 'Все производства', 'Жалобы ФАС', 'Данные о жалобах в отношении организации в ФАС отсутствуют.', 'Лицензии', 'Сведения о лицензиях в отношении ООО "ИНВЕСТСТРОЙПРОЕКТ" отсутствуют.', 'Конкуренты по величине баланса', 'Наименование компании', 'Баланс, ₽', 'ООО "ЭГИДА"', '451 835 000', 'ООО "СТРОЙПРОЕКТ"', '451 686 000', 'ООО «СЗ «АСК-ВОДРЕМ»', '451 665 000', 'АО "ТСМ"', '451 401 000', 'Учредители', 'Согласно данным ЕГРЮЛ учредителями ООО "ИНВЕСТСТРОЙПРОЕКТ" являются: 1 российское юридическое лицо3 физических лица', 'Валиев Ильмир Исламович', 'Доля:', '3 696 ₽ (33.6%)', 'ИНН:', '162201225231', 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЭКОСТРОЙИНЖИНИРИНГ"', 'Доля:', '2 882 ₽ (26.2%)', 'ИНН:', '1657220029', 'ОГРН:', '1161690070123', 'Зайнутдинов Руслан Рустамович', 'Доля:', '2 211 ₽ (20.1%)', 'ИНН:', '162700654540', 'Валиев Ильнур Исламович', 'Доля:', '2 211 ₽ (20.1%)', 'ИНН:', '162200912337', 'Все 4 учредителя', 'Ваша вечная визитка', 'Удобный способ обмена', 'контактами в одно касание', 'Подробнее', 'Связи', 'Выявлено 19 связей с организациями и предпринимателями', 'По учредителю', '14', 'По руководителю', '5', 'Все связи', 'Арбитражные дела', 'Сведения об участии в судебных процессах: 1 открытое и 39 закрытых дел', '№ А65-19624/2023', 'ЗАКРЫТО', 'от 11.07.2023', 'о несостоятельности (банкротстве) организаций и граждан', 'Сумма: 1 950 000 ₽', 'Истец: Общество с ограниченной ответственность "ИнвестСтройПроект", г.Казань', 'Ответчик: Общество с ограниченной ответственность "РЕА-Строй", г.Казань', '№ А65-19331/2023', 'ЗАКРЫТО', 'от 07.07.2023', 'экономические споры по административным и иным публичным правоотношениям (исключая споры об административных правонарушениях)', 'Сумма: -', 'Истец: Общество с ограниченной ответственность "ИнвестСтройПроект", г.Казань', 'Ответчик: Управление Федеральной антимонопольной службы по Республике Татарстан, г.Казань', '№ А65-19330/2023', 'ЗАКРЫТО', 'от 07.07.2023', 'экономические споры по административным и иным публичным правоотношениям (исключая споры об административных правонарушениях)', 'Сумма: -', 'Истец: Общество с ограниченной ответственность "ИнвестСтройПроект", г.Казань', 'Ответчик: Управление Федеральной антимонопольной службы по Республике Татарстан, г.Казань', '№ А65-36356/2022', 'ЗАКРЫТО', 'от 26.12.2022', 'экономические споры по гражданским правоотношениям', 'Сумма: 336 447 ₽', 'Истец: Федеральное казенное учреждение "Федеральное управление автомобильных дорог Волго-Вятского региона Федерального дорожного агентства", г.Казань', 'Ответчик: Общество с ограниченной ответственность "ИнвестСтройПроект", г.Казань', 'Все дела', 'Филиалы и представительства', 'Сведения о филиалах для ООО "ИНВЕСТСТРОЙПРОЕКТ" отсутствуют.', 'Одноименные компании', 'Наименование компании и руководитель', 'ООО "ИНВЕСТСТРОЙПРОЕКТ" , Андрей Николаевич Зацепин', 'ООО "ИНВЕСТСТРОЙПРОЕКТ"', 'ООО "ИНВЕСТСТРОЙПРОЕКТ" , Марина Александровна Захарова', 'ООО "ИНВЕСТСТРОЙПРОЕКТ" , Андрей Николаевич Корниенко', 'Похожие компании по ИНН', 'Наименование компании', 'Инн', 'ООО "УК "СБК"', '1657220068', 'ООО "САЛАМАТ РИТЕЙЛ"', '1657220082', 'ООО "ПЛОВБЕРИ ЕКБ"', '1657220100', 'ООО "ЭМПАСТА"', '1657220117', 'Секреты компании', 'Сведения, предсказанные искусственным интеллектом приложения TenChat', 'Вероятность проверки:', 'Срок задержки оплаты:', 'Просроченные контракты:', 'Блокировка банк.счетов:', 'Количество клиентов:', 'Получить информацию', 'Отзывы о компании', 'Обновлено 20.08.2023', 'ФКУ УПРДОР "ПРИКАМЬЕ" (Клиент)', '01.10.2021', '5,0', 'Фирма без нареканий все сделали по обязательству 1212600032320000030 "Выполнение работ по объекту: «Расходы на мероприятия по повышению уровня обустройства автомобильных дорог федерального значения. Устройство стационарного электрического освещения на автомобильной дороге М-7 "Волга" Москва – Владимир – Нижний Новгород – Казань – Уфа, подъезд к городам Ижевск и Пермь на участках км 82+300 – км 83+000 н.п. Можга, км 93+900 – км 94+800 н.п. Горняк, км 263+450 – км 267+900 н.п. Сундур, н.п. Игра, Удмуртская Республика»". Отлично уложились по срокам. Будем работать и дальше.', 'ФКУ "ВОЛГО-ВЯТСКУПРАВТОДОР" (Клиент)', '06.12.2020', '5,0', 'Контракт "Капитальный ремонт моста через реку С.Овраг на км 220+283 (левый) автомобильной дороги М-5  "Урал"- Москва-Рязань- Пенза-Самара-Уфа-Челябинск, подъезд к городу Ульяновск, Ульяновская область" был выполнен без проблем. Спасибо. Желаем успешного развития!', 'Все отзывы Добавить отзыв', 'События', 'Обновлено 20.08.2023', 'Победа в тендерах', '10.08.2023', '| Госконтракты', '№ 0311100007223000079', 'Содержание искусственных сооружений на автомобильных дорогах: Р-176 "Вятка" Чебоксары - Йошкар-Ола - Киров - Сыктывкар на участках км 19+008 - км 87+152, км 94+600 - км 135+087; Р-176 "Вятка" Чебоксары - Йошкар-Ола - Киров - Сыктывкар, обход г. Йошкар-Ола на участке км 18+400 - км 47+965; А-295 Йошкар-Ола - Зеленодольск - автомобильная дорога М-7 "Волга" на участке км 8+123 - км 95+566; Р-177 "Поветлужье" Нижний Новгород - Йошкар-Ола на участке км 186+534 - км 353+754, Республика Марий Эл', 'Победа в тендерах', '10.08.2023', '| Госконтракты', '№ 0311100007223000078', 'Содержание искусственных сооружений на автомобильных дорогах: М-7 "Волга" Москва - Владимир - Нижний Новгород - Казань - Уфа на участке км 735+683 - км 785+817; А-295 Йошкар-Ола - Зеленодольск - автомобильная дорога М-7 "Волга" на участке км 95+566 - км 126+279, Республика Татарстан', 'Победа в тендерах', '26.06.2023', '| Госконтракты', '№ 0311100007223000065', 'Содержание искусственных сооружений на автомобильных дорогах М-7 "Волга" Москва - Владимир - Нижний Новгород - Казань - Уфа на участке км 735+683 - км 785+817; А-295 Йошкар-Ола - Зеленодольск - автомобильная дорога М-7 "Волга" на участке км 95+566 - км 126+279, Республика Татарстан', 'Победа в тендерах', '25.06.2023', '| Госконтракты', '№ 0311100007223000064', 'Содержание искусственных сооружений на автомобильных дорогах Р-176 "Вятка" Чебоксары - Йошкар-Ола - Киров - Сыктывкар на участках км 19+008 - км 87+152, км 94+600 - км 135+087; Р-176 "Вятка" Чебоксары - Йошкар-Ола - Киров - Сыктывкар, обход г. Йошкар-Ола на участке км 18+400 - км 47+965; А-295 Йошкар-Ола - Зеленодольск - автомобильная дорога М-7 "Волга" на участке км 8+123 - км 95+566; Р-177 "Поветлужье" Нижний Новгород - Йошкар-Ола на участке км 186+534 - км 353+754, Республика Марий Эл', 'Исторические сведения (85 изменений)', 'Напишите генеральному директору', 'Общайтесь', 'с банками и деловыми партнёрами', 'Предлагайте', 'сотрудничество любому контрагенту', 'Отслеживайте', 'любые события по конкурентам', 'Главная >', 'Проверка контрагентов >', 'ООО "ИНВЕСТСТРОЙПРОЕКТ"', 'Госзакупки', 'Поиск тендера', 'Банковские гарантии', 'Кредиты на исполнение контракта', 'Сопровождение торгов', 'Поиск контрагента по ИНН', 'Финансовый маркетплейс', 'Тендерные займы', 'РКО', 'Инвестиции', 'Частным клиентам', 'Кредиты', 'TenChat', 'Торги по банкротству', 'Субподряды', 'Агентам и партнерам', 'Агентская программа', 'Подключение партнеров', 'Профессионалам', 'Начинающим', 'О проекте', 'Контакты', 'Документы', 'Миссия', 'Руководство', 'Вакансии', 'Предложения, жалобы, новые идеи: Написать напрямую председателю правления ВБЦ', 'Россия, г. Москва, 123290, ул. Мукомольный проезд 4а, стр.2', '© 2016–2023, ООО «ВБЦ», ООО «ВБЦ Лаб» официальный сайт, лицензия Минкомсвязи № 144842 от 8 июня 2016 г.', '8 (800) 300-43-43', 'client@vbankcenter.ru', 'Пользовательское соглашение и Регламент ЭДО Политика конфиденциальности', 'Нам важно Ваше мнение о нашей работе!', 'Перейти к опросу', 'ООО ВБЦ Лаб - резидент ИТ-кластера инновационного проекта Сколково, Маркетплейс ВБЦ включен в реестр российского ПО', 'Лучший финансовый маркетплейс 2020 по версии журнала NBJ']
        # print(full_info_leasee_vbc)
        if 'Все учредители' in full_info_leasee_vbc:
            index_konwch = 'Все учредители'
        elif 'Все 2 учредителя' in full_info_leasee_vbc:
            index_konwch = 'Все 2 учредителя'
        elif 'Все 3 учредителя' in full_info_leasee_vbc:
            index_konwch = 'Все 3 учредителя'
        elif 'Все 4 учредителя' in full_info_leasee_vbc:
            index_konwch = 'Все 4 учредителя'
        else:
            index_konwch = ''

        if ip_or_kfh != 'Да' and result[0]['data']['opf']['short'] not in ['НАО', 'ПАО']:
            full_info_leasee_vbc_out_1_leader = full_info_leasee_vbc[
                                                full_info_leasee_vbc.index(
                                                    'Сотрудники') + 1:full_info_leasee_vbc.index(
                                                    index_konwch) + 1]
            list_info = full_info_leasee_vbc_out_1_leader[
                        full_info_leasee_vbc_out_1_leader.index('Учредители') + 2:]
            count = 0
            for elem in list_info:
                count += 1
                if elem == 'Доля:':
                    del list_info[count - 1]
                if elem == 'ИНН:':
                    del list_info[count - 1]
            ls = list_info
            try:
                index = ls.index('ОГРН:')
                my_list = ls[:index] + ls[index + 2:]
                # print(my_list[:-1])
                # print('Сработало тут1')
                try:
                    # print(f'vyvod my_list {my_list[:-1]}')
                    index = my_list[:-1].index('ОГРН:')
                    my_list = my_list[:-1][:index] + my_list[:-1][index + 1:]
                    # print(my_list[:-1])
                    # print('Сработало тут2')
                except:
                    pass
            except:
                my_list = ls
                # print(my_list[:-1])
                # print('Сработало тут3')
            fio_list, dolya_list, inn_list = [], [], []
            count_more = -1
            for word in my_list[:-1]:
                count_more += 1
                if count_more == 0 or count_more % 3 == 0:
                    fio_list.append(word)
                if count_more == 1 or count_more % 3 == 1:
                    dolya_list.append(word)
                    # print(dolya_list)
                if count_more == 2 or count_more % 3 == 2:
                    inn_list.append(word)
            pattern = r'\d+\.\d+%'
            for i in range(len(dolya_list)):
                index = dolya_list[i].index('(')
                dolya_list[i] = dolya_list[i][index + 1:].replace('%', '').replace(')', '').replace('.', ',')
            # print(f'здесь список учредов {fio_list}')
            # print(f'здесь список доли в УК {dolya_list}')
            # print(f'здесь список ИНН учредов {inn_list}')

        try:
            index_inn_dir_leasee = full_info_leasee_vbc.index('Банковские счета')
            inn_dir_leasee = full_info_leasee_vbc[index_inn_dir_leasee + 5].replace('ИНН: ', '')
        except:
            inn_dir_leasee = ''

        try:
            index_phone_leasee = full_info_leasee_vbc.index('Телефон: ')
            phone_leasee = full_info_leasee_vbc[index_phone_leasee + 1]
            # print(f'Здесь брать телефон лизингополучателя {phone_leasee}')
        except:
            phone_leasee = '-'
            # print(phone_leasee)

        try:
            index_email_leasee = full_info_leasee_vbc.index('E-mail: ')
            email_leasee = full_info_leasee_vbc[index_email_leasee + 1]
            # print(f'Здесь брать email лизингополучателя {email_leasee}')
        except:
            email_leasee = '-'
            # print(email_leasee)

        try:
            index_main_activity_leasee = full_info_leasee_vbc.index('Основной вид деятельности')
            main_activity_leasee = full_info_leasee_vbc[index_main_activity_leasee + 1]
            start_index = main_activity_leasee.find('Все виды деятельности')
            if start_index != -1:
                # Если найдено, удаляем все после этой позиции
                main_activity_leasee = main_activity_leasee[:start_index]
            # print(f'Здесь брать основной ОКВЭД лизингополучателя {main_activity_leasee}')

        except:
            main_activity_leasee = 'Не найдено'
            # print(main_activity_leasee)

        try:
            index_ustav_capital = full_info_leasee_vbc.index('Уставный капитал, ₽')
            ustav_capital = full_info_leasee_vbc[index_ustav_capital + 1].replace(' тыс', '000')
            # print(f'Здесь брать УК лизингополучателя {ustav_capital}')
        except:
            ustav_capital = '-'
            # print(f'Уставный капитал {ustav_capital} , возможно клиент ИП или КФХ')
        logging.info(f"({current_user}) Этап 3.")

        result_seller1 = dadata.find_by_id("party", inn_seller1)
        # print(result_seller1)

        krakt_name_seller1 = result_seller1[0]['data']['name']['short_with_opf']
        # print(f'Здесь брать краткое наименование Продавца №1 {krakt_name_seller1}')

        address_seller1 = result_seller1[0]['data']['address']['unrestricted_value']
        # print(f'Здесь брать юр адрес Продавца №1 {address_seller1}')

        # print(len(inn_seller2))
        if len(inn_seller2) >= 1 and inn_seller2 is not None:
            result_seller2 = dadata.find_by_id("party", inn_seller2)
            # print(result_seller2)

            krakt_name_seller2 = result_seller2[0]['data']['name']['short_with_opf']
            # print(f'Здесь брать краткое наименование Продавца №2 {krakt_name_seller2}')

            address_seller2 = result_seller2[0]['data']['address']['unrestricted_value']
            # print(f'Здесь брать юр адрес Продавца №2 {address_seller2}')

        if len(inn_seller3) >= 1 and inn_seller3 is not None:
            result_seller3 = dadata.find_by_id("party", inn_seller3)
            # print(result_seller3)

            krakt_name_seller3 = result_seller3[0]['data']['name']['short_with_opf']
            # print(f'Здесь брать краткое наименование Продавца №3 {krakt_name_seller3}')

            address_seller3 = result_seller3[0]['data']['address']['unrestricted_value']
            # print(f'Здесь брать юр адрес Продавца №3 {address_seller3}')

        if len(inn_seller4) >= 1 and inn_seller4 is not None:
            result_seller4 = dadata.find_by_id("party", inn_seller4)
            # print(result_seller4)

            krakt_name_seller4 = result_seller4[0]['data']['name']['short_with_opf']
            # print(f'Здесь брать краткое наименование Продавца №4 {krakt_name_seller4}')

            address_seller4 = result_seller4[0]['data']['address']['unrestricted_value']
            # print(f'Здесь брать юр адрес Продавца №4 {address_seller4}')

    def zapolnenie_zayvki_ankety(inn_leasee, path_application):
        logging.info(f"({current_user}) Этап 4.")
        try:
            # сейчас будем заполнять заявку, вносить данные по лп
            wb = openpyxl.load_workbook(rf'{path_application}',
                                        read_only=False)
            # заполняем страницу Заявление
            sheet_zayavlenie = wb['Заявление']
            sheet_zayavlenie['A5'].value = full_name_leasee
            sheet_zayavlenie['D6'].value = inn_kpp_leasee
            sheet_zayavlenie['B1'].value = dt.today().strftime(f"%d.%m.%Y")
            if ip_or_kfh == 'Да':
                sheet_zayavlenie['D6'].value = inn_leasee
            # print(sheet_zayavlenie['A6'].value)
            # print(sheet_zayavlenie['C7'].value)
            sheet_zayavlenie['H6'].value = address_leasee
            # print(sheet_zayavlenie['E7'].value)

            sheet_zayavlenie['A10'].value = krakt_name_seller1
            sheet_zayavlenie['C11'].value = inn_seller1
            sheet_zayavlenie['G11'].value = address_seller1
            if len(inn_seller2) >= 1 and inn_seller2 is not None:
                sheet_zayavlenie['A12'].value = krakt_name_seller2
                sheet_zayavlenie['C13'].value = inn_seller2
                sheet_zayavlenie['G13'].value = address_seller2
            if len(inn_seller3) >= 1 and inn_seller3 is not None:
                sheet_zayavlenie['A14'].value = krakt_name_seller3
                sheet_zayavlenie['C15'].value = inn_seller3
                sheet_zayavlenie['G15'].value = address_seller3
            if len(inn_seller4) >= 1 and inn_seller4 is not None:
                sheet_zayavlenie['A16'].value = krakt_name_seller4
                sheet_zayavlenie['C17'].value = inn_seller4
                sheet_zayavlenie['G17'].value = address_seller4

            counter_1 = 24
            for number in range(25, sheet_zayavlenie.max_row + 2):
                counter_1 += 1
                if sheet_zayavlenie[
                    f'B{number}'].value == 'Место эксплуатации предмета лизинга (для автотранспорта место стоянки/хранения) полный фактический адрес:':
                    sheet_zayavlenie[f'A{number + 1}'].value = address_leasee
                    # print(sheet_zayavlenie[f'A{number + 1}'].value)
                if sheet_zayavlenie[f'A{number}'].value == '(должность руководителя организации Заявителя)':
                    sheet_zayavlenie[f'A{number - 1}'].value = leader_leasee
                    # print(sheet_zayavlenie[f'B{number - 1}'].value)
                if sheet_zayavlenie[f'O{number}'].value == '(расшифровка подписи)':
                    sheet_zayavlenie[f'O{number - 1}'].value = formatted_name_leader_leasee
                    # print(sheet_zayavlenie[f'H{number - 1}'].value)
                if sheet_zayavlenie[f'G{number}'].value == 'ИНН:':
                    sheet_zayavlenie[f'H{number}'].value = inn_dir_leasee

                # заполнение поручителей, автоматом поставил всех учредов
                if ip_or_kfh != 'Да':
                    if sheet_zayavlenie[f'B{number}'].value == 'Наименование поручителя ⃰ ':
                        for row_num, fio in enumerate(fio_list, start=1):
                            sheet_zayavlenie.cell(row=row_num + counter_1, column=2, value=fio)
                        # print(sheet_zayavlenie.cell(row=row_num + counter_1, column=2, value=fio).value)
                    if sheet_zayavlenie[f'J{number}'].value == 'ИНН':
                        for row_num, inn in enumerate(inn_list, start=1):
                            sheet_zayavlenie.cell(row=row_num + counter_1, column=10, value=inn)

                        # print(sheet_zayavlenie.cell(row=row_num + counter_1, column=6, value=inn).value)
                if ip_or_kfh == 'Да':
                    if sheet_zayavlenie[f'B{number}'].value == 'Наименование поручителя ⃰ ':
                        sheet_zayavlenie[f'B{number + 1}'].value = fio_leader
                        # print(sheet_zayavlenie[f'B{number + 1}'].value)
                    if sheet_zayavlenie[f'J{number}'].value == 'ИНН':
                        sheet_zayavlenie[f'J{number + 1}'].value = inn_leasee
                        # print(sheet_zayavlenie[f'F{number + 1}'].value)
                    if sheet_zayavlenie[f'A{number}'].value == '(должность руководителя организации Заявителя)':
                        if type_business == 'Индивидуальный предприниматель' or type_business == 'ИП':
                            sheet_zayavlenie[f'A{number - 1}'].value = type_business
                        else:
                            sheet_zayavlenie[f'A{number - 1}'].value = 'Глава'

            # заполняем страницу Анкета Стр.1
            sheet_anketa_1_list = wb['Анкета Стр.1']
            sheet_anketa_1_list['F7'].value = ogrn_leasee
            # print(sheet_anketa_1_list['F7'].value)
            sheet_anketa_1_list['H7'].value = okato_leasee
            # print(sheet_anketa_1_list['H7'].value)
            sheet_anketa_1_list['J7'].value = okpo_leasee
            # print(sheet_anketa_1_list['J7'].value)
            sheet_anketa_1_list['E8'].value = date_regist
            # print(sheet_anketa_1_list['E8'].value)
            sheet_anketa_1_list['J9'].value = ustav_capital
            # print(sheet_anketa_1_list['J9'].value)
            sheet_anketa_1_list['A6'].value = full_krakt_name_leasee
            # print(sheet_anketa_1_list['A6'].value)

            counter_2_anketa = 7
            for number in range(8, sheet_anketa_1_list.max_row + 2):
                counter_2_anketa += 1
                # заполняем инфу по учредам, не более 4-х должно быть
                if ip_or_kfh == 'Нет':
                    if sheet_anketa_1_list[
                        f'B{number}'].value == 'полное наименование акционера/участника/члена/товарища с указанием организационно-правовой формы (полностью Ф.И.О. для физических лиц):':
                        for row_num, fio in enumerate(fio_list, start=1):
                            sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=2, value=fio)
                        # print(sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=2, value=fio).value)
                    if sheet_anketa_1_list[f'G{number}'].value == 'ИНН':
                        # print(counter_2_anketa)
                        for row_num, inn in enumerate(inn_list, start=1):
                            sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=7, value=inn)
                        # print(sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=7, value=inn).value)
                    if sheet_anketa_1_list[f'I{number}'].value == 'доля в уставном капитале, в %':
                        for row_num, dolya in enumerate(dolya_list, start=1):
                            # dolya_value = float(dolya)
                            sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=9, value=dolya)
                        # print(sheet_anketa_1_list.cell(row=row_num + counter_2_anketa + 1, column=9).value)

                if sheet_anketa_1_list[f'A{number}'].value == '1.7         Телефон:':
                    sheet_anketa_1_list[f'C{number}'].value = phone_leasee
                    # print(sheet_anketa_1_list[f'C{number}'].value)
                if sheet_anketa_1_list[f'E{number}'].value == '1.8 Эл. почта:':
                    sheet_anketa_1_list[f'F{number}'].value = email_leasee
                    # print(sheet_anketa_1_list[f'F{number}'].value)
                if sheet_anketa_1_list[f'B{number}'].value == 'ФИО:':
                    sheet_anketa_1_list[f'C{number}'].value = fio_leader
                    # print(sheet_anketa_1_list[f'C{number}'].value)
                if sheet_anketa_1_list[f'B{number}'].value == 'ОКВЭД с расшифровкой:':
                    sheet_anketa_1_list[f'E{number}'].value = main_activity_leasee
                    # print(sheet_anketa_1_list[f'E{number}'].value)

            application_filename = fr'{temporary_path}\Заявка с заключением {inn_leasee}.xlsx'
            wb.save(application_filename)
            application_filename_download = fr'{path_for_download}\Заявка с заключением {inn_leasee}.xlsx'
            logging.info(f"({current_user}) Все успешно сохранилось!")
            return application_filename_download
        except Exception as ex:
            logging.info(ex, exc_info=True)
            raise ValueError

    parser_info_leasee(inn_leasee)  # берет инфу из инета по лизингополучателю
    application_filename = zapolnenie_zayvki_ankety(inn_leasee,
                                                    path_application)  # заполняет эксель данными из инета по лизингополучателю

    return application_filename


def start_filling_agreement(inn_leasee, path_application, path_graphic, signatory, investor, currency_list,
                            who_is_insure, grafic, pl, number_dl, inn_seller, type_pl):
    dadata = Dadata(DADATA_TOKEN)
    result = dadata.find_by_id("party", inn_leasee)

    full_krakt_name_leasee = result[0]['data']['name']['short_with_opf'].replace('"', '')

    dir_path = fr'webapp\static\agreements\{full_krakt_name_leasee} {inn_leasee}\{dt.today().strftime(f"%d.%m.%Y")}'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    data_xlsx = read_xlsx(path_application, pl)
    for i in range(len(data_xlsx)):
        print(f'#{i} -> {data_xlsx[i]}')

    print(pl)
    print(inn_seller)

    formatted_name_leader_leasee = data_xlsx[17]
    full_name_leasee = data_xlsx[22]
    full_krakt_name_leasee = data_xlsx[8]
    inn_kpp_leasee = data_xlsx[21]
    address_leasee = data_xlsx[20]
    address_leasee_expluatazia = data_xlsx[19]
    predmet_lizinga = pl
    inn_seller_list = inn_seller
    price_predmet_lizinga = data_xlsx[15]
    ogrn_leasee = data_xlsx[13]
    okato_leasee = data_xlsx[12]
    okpo_leasee = data_xlsx[11]
    date_regist = data_xlsx[10]
    ustav_capital = data_xlsx[9]
    phone_leasee = data_xlsx[7]
    email_leasee = data_xlsx[6]
    fio_leader = data_xlsx[5]
    main_activity_leasee = data_xlsx[4]
    rekvizit_leasee_bank = data_xlsx[3]
    rekvizit_leasee_shet = data_xlsx[2]
    rekvizit_leasee_cs_shet = data_xlsx[1]
    rekvizit_leasee_bik = data_xlsx[0]
    leader_leasee = data_xlsx[18]

    # Чтение заявки и анкеты

    vikup = ''
    vigodo = ''

    input_raschet_path = rf'{path_graphic}'

    def create_dl_dkp(inn_leasee, path_application, path_graphic, signatory, investor, currency_list, who_is_insure,
                      grafic, pl, number_dl, inn_seller):
        nonlocal leader_leasee, vikup, vigodo
        if signatory == 'Каюмов А. Д.':
            a_lkmb = 'Директор'
            lkmb_podpisant = 'Каюмов А. Д.'
            preambula_dolj_lkmb = 'Директора'
            preambula_fio_lkmb = 'Каюмова Айрата Дамировича'
            doverka_ustav_list = 'Устава'
            deystvuysh_list = 'действующего'
        elif signatory == 'Габдрахманов Р. Р.':
            a_lkmb = 'Заместитель директора'
            lkmb_podpisant = 'Габдрахманов Р. Р.'
            preambula_dolj_lkmb = 'Заместителя директора'
            preambula_fio_lkmb = 'Габдрахманова Рината Рафаэлевича'
            doverka_ustav_list = 'Доверенности от «17» марта 2020 года, удостоверенной Мальченковой  Евгенией Николаевной, нотариусом Казанского нотариального округа Республики Татарстан, зарегистрированной в реестре нотариальных действий за № 16/64-н/16-2020-7-317(бланк 16 АА 5665323)'
            deystvuysh_list = 'действующего'
        else:
            a_lkmb = 'Заместитель директора по финансам'
            lkmb_podpisant = 'Хасанова Д. Р.'
            preambula_dolj_lkmb = 'Заместителя директора по финансам'
            preambula_fio_lkmb = 'Хасановой Динары Ринатовны'
            doverka_ustav_list = 'Доверенности от «17» марта 2020 года, удостоверенной Мальченковой  Евгенией Николаевной, нотариусом Казанского нотариального округа Республики Татарстан, зарегистрированной в реестре нотариальных действий за № 16/64-н/16-2020-7-317(бланк 16 АА 5665323)'
            deystvuysh_list = 'действующей'
        if leader_leasee.upper() == 'директор'.upper():
            leader_leasee_rod_padezh = 'Директора'
        elif leader_leasee.upper() == 'генеральный директор'.upper():
            leader_leasee_rod_padezh = 'Генерального директора'
        elif leader_leasee.upper() == 'исполняющий обязанности директора'.upper():
            leader_leasee_rod_padezh = 'ИО директора'
        else:
            leader_leasee_rod_padezh = ''

        # запускается функция по замене ФИО подписанта лизингополучателя
        put_padezh_podpisant = ''

        def rod_padezh_fio_leader(fio):
            # dadata = Dadata(DADATA_TOKEN, DADATA_SECRET)
            logging.info(f"({fio})")
            # put_padezh_podpisant = DADATA_BASE.clean("name", fio)
            put_padezh_podpisant = {'source': 'Ибнеев Рустем Шамилевич', 'result': 'Ибнеев Рустем Шамилевич',
                                    'result_genitive': 'Ибнеева Рустема Шамилевича',
                                    'result_dative': 'Ибнееву Рустему Шамилевичу',
                                    'result_ablative': 'Ибнеевым Рустемом Шамилевичем', 'surname': 'Ибнеев',
                                    'name': 'Рустем',
                                    'patronymic': 'Шамилевич', 'gender': 'М', 'qc': 0}  # mock
            print(put_padezh_podpisant)
            return put_padezh_podpisant
            # print(f" Здесь пол М или Ж: Итого {put_padezh_podpisant['gender']}")
            # print(f" Здесь родительный падеж подписанта: Итого {put_padezh_podpisant['result_genitive']}")

        print('19101')
        rod_padezh_fio_leader = rod_padezh_fio_leader(data_xlsx[5])
        try:
            put_padezh_podpisant_rg = rod_padezh_fio_leader['result_genitive']
        except:
            put_padezh_podpisant_rg = ''
        print(f'123 {put_padezh_podpisant_rg}')
        doverka_ustav_leasee = 'Устава'
        for elem in full_name_leasee.split():
            if elem in ['Индивидуальный', 'предприниматель', 'хозяйства']:
                doverka_ustav_leasee = f'Свидетельства о государственной регистрации физического лица в качестве индивидуального предпринимателя серия __ № _________ от {date_regist}, ОГРНИП {ogrn_leasee}'

        deystvuysh_list_leasee = 'действующей'
        try:
            if rod_padezh_fio_leader['gender'] == 'М':
                deystvuysh_list_leasee = 'действующего'
                if result[0]['data']['opf']['short'] in ['ИП', 'КФХ', 'ГКФХ']:
                    deystvuysh_list_leasee = 'действующий'
                imenyemoe = 'именуемый'
        except:
            try:
                if result[0]['data']['opf']['short'] in ['ИП', 'КФХ', 'ГКФХ']:
                    deystvuysh_list_leasee = 'действующая'
            except:
                deystvuysh_list_leasee = 'действующей'
            imenyemoe = 'именуемая'
        # deystvuysh_list_leasee = 'действующей' if fio_leader.split()[0][-1].lower() == 'а' else 'действующего'

        if investor in ['ПАО «МКБ»', 'ООО «ЛКМБ-РТ»']:
            vigodo = 'Лизингодатель'
        else:
            vigodo = investor

        print('1912132')
        r_chet_lkmb = ''
        bank_rekv_lkmb = ''
        kor_chet_lkmb = ''
        bik_lkmb = ''

        if investor.upper() == 'ПАО АКБ «МЕТАЛЛИНВЕСТБАНК»'.upper():
            r_chet_lkmb = '40701810000990000052'
            bank_rekv_lkmb = 'ПАО АКБ «МЕТАЛЛИНВЕСТБАНК»'
            kor_chet_lkmb = '30101810300000000176'
            bik_lkmb = '044525176'
        elif investor.upper() == 'ПАО «МКБ»'.upper():
            r_chet_lkmb = '40701810900760000034'
            bank_rekv_lkmb = 'ПАО «МОСКОВСКИЙ КРЕДИТНЫЙ БАНК»'
            kor_chet_lkmb = '30101810745250000659'
            bik_lkmb = '044525659'
        elif investor.upper() == 'АО «Инвестторгбанк»'.upper():
            r_chet_lkmb = '40701810071010300002'
            bank_rekv_lkmb = 'АО «Инвестторгбанк»'
            kor_chet_lkmb = '30101810645250000267'
            bik_lkmb = '044525267'
        elif investor.upper() == 'АО «АЛЬФА-БАНК»'.upper():
            r_chet_lkmb = '40701810129930000005'
            bank_rekv_lkmb = 'ФИЛИАЛ «НИЖЕГОРОДСКИЙ» АО «АЛЬФА-БАНК»'
            kor_chet_lkmb = '30101810200000000824'
            bik_lkmb = '042202824'
        elif investor.upper() == 'АО «ПЕРВОУРАЛЬСКБАНК»'.upper():
            r_chet_lkmb = '40701810000010055037'
            bank_rekv_lkmb = 'АО «ПЕРВОУРАЛЬСКБАНК»'
            kor_chet_lkmb = '30101810565770000402'
            bik_lkmb = '046577402'
        elif investor.upper() == 'АО «СОЛИД БАНК»'.upper():
            r_chet_lkmb = '40701810105040011167'
            bank_rekv_lkmb = 'Московский филиал АО «СОЛИД БАНК»'
            kor_chet_lkmb = '30101810845250000795'
            bik_lkmb = '044525795'
        elif investor.upper() == 'АО КБ «УРАЛ ФД»'.upper():
            r_chet_lkmb = '40701810000000000962'
            bank_rekv_lkmb = 'АО КБ «УРАЛ ФД»'
            kor_chet_lkmb = '30101810800000000790'
            bik_lkmb = '045773790'
        else:
            r_chet_lkmb = '40702810100020002464'
            bank_rekv_lkmb = 'ПАО «АК БАРС» БАНК г. Казань'
            kor_chet_lkmb = '30101810000000000805'
            bik_lkmb = '049205805'

        currency = ''
        if currency_list == 'Рубль':
            currency_test = 'рублей'
        elif currency_list == 'Китайский юань':
            currency_test = 'юаней'
        elif currency_list == 'Доллар США':
            currency_test = 'долларов США'

        wr_rub_usd = {'рублей': 'рублях', 'доллары США': 'долларах США', 'ЕВРО': 'ЕВРО', 'юань': 'юанях',
                      'китайский юань': 'китайских юанях', 'рубль': 'рублях', 'доллары': 'долларах',
                      'руб.': 'рублях',
                      'юани': 'юанях', 'юаней': 'юанях', 'долларов США': 'долларах США'}
        # print(currency)
        # print(wr_rub_usd)
        print('1910')
        leader_leasee_pod = leader_leasee
        inn_kpp1 = 'ИНН/КПП'
        ogrnip = ''
        if result[0]['data']['opf']['short'] in ['ИП', 'ГКФХ', 'КФХ']:
            inn_kpp1 = 'ИНН'
            ogrnip = f'ОГРНИП {ogrn_leasee}'
            leader_leasee_pod = ''
            put_padezh_podpisant_rg = ''
        else:
            imenyemoe = 'именуемое'
        print(f'123213 {put_padezh_podpisant_rg}')
        vikup = '1000'
        pl_entry = pl

        price_entry = price_predmet_lizinga
        if vikup == '1000':
            punkt_4_6 = '4.6. Выкупная цена предмета лизинга составляет 1 000,00 (Одна тысяча) рублей, в том числе НДС.'
        else:
            punkt_4_6 = '4.6. Выкупная цена предмета лизинга, равная остаточной стоимости этого предмета лизинга, рассчитывается в соответствии с действующим законодательством Российской Федерации с учетом согласованной нормы амортизации. При этом выкупные платежи, уплаченные Лизингополучателем в составе лизинговых платежей в соответствии с Приложением № 1 к настоящему договору в качестве выкупных платежей, принимаются в зачет оплаты выкупной цены предмета лизинга. В случае расторжения настоящего договора по вине Лизингополучателя, в случае отказа от приемки предмета лизинга уплаченные Лизингополучателем выкупные платежи возвращению не подлежат, а удерживаются в качестве штрафа.'

        if investor == 'АО «Инвестторгбанк»':
            punkt_7_8 = '\n'.join([
                '7.8. Лизингополучатель уведомлен:                                                                       ',
                '- что предмет лизинга обременен залогом АО «Инвестторгбанк» по кредитному договору, в рамках которого',
                'осуществляется финансирование лизинговой сделки, и что права требования на получение платежей по договору',
                'лизинга переданы в залог Банку;                                                                                          ',
                '- что Лизингополучатель при получении соответствующего уведомления от Банка (залогодержателя) обязан',
                'исполнять свое обязательство по договору лизинга Залогодержателю. При этом уведомление направляется любым из',
                'способов, определенных договором залога.'])
        else:
            punkt_7_8 = 'УДАЛИТЬ'

        suma_dann = ''
        print('191919')

        def chislo_propis():
            nonlocal suma_dann
            suma_chislo = price_entry

            def number_to_words(suma_chislo):
                try:
                    # Разбиваем строку на целую и десятичную часть
                    suma_chislo = str(round(float(suma_chislo), 2)).replace(',', '.') if \
                        str(round(float(suma_chislo), 2)).replace(',', '.')[-3] == '.' else str(
                        round(float(suma_chislo), 2)).replace(',', '.') + '0'
                    parts = suma_chislo.split(".")
                    integer_part = parts[0]
                    decimal_part = parts[1] if len(parts) > 1 else "00"

                    # Преобразуем целую часть в число прописью
                    integer_words = num2words(int(integer_part), lang='ru')

                    # Определяем правильную форму для "рублей"
                    if 10 < float(integer_part) % 100 < 20:
                        valute_rub = "рублей"
                    elif float(integer_part) % 10 == 1:
                        valute_rub = "рубль"
                    elif 1 < float(integer_part) % 10 < 5:
                        valute_rub = "рубля"
                    else:
                        valute_rub = "рублей"

                    # Преобразуем десятичную часть в число прописью
                    if currency_list == 'Рубль':
                        decimal_words = num2words(int(decimal_part), lang='ru', to='currency', currency='RUB')
                    else:
                        decimal_words = num2words(int(decimal_part), lang='ru')

                    # Определяем правильную форму для "копеек"
                    if 10 < float(decimal_part) % 100 < 20:
                        valute_copeyka = "копеек"
                    elif float(decimal_part) % 10 == 1:
                        valute_copeyka = "копейка"
                    elif 1 < float(decimal_part) % 10 <= 4:
                        valute_copeyka = "копейки"
                    else:
                        valute_copeyka = "копеек"

                    # Формируем итоговую строку
                    if currency_list == 'Рубль':
                        suma_dann = f"{integer_words} {valute_rub} {decimal_words}".strip().replace('ноль рублей',
                                                                                                    '').replace(' ,',
                                                                                                                '')
                    elif currency_list == 'Китайский юань':
                        suma_dann = f"{integer_words} целых {decimal_words} сотых китайских юаней"
                    elif currency_list == 'Доллар США':
                        suma_dann = f"{integer_words} целых {decimal_words} сотых долларов США"
                    return suma_dann
                except ValueError:
                    return "Неверный формат числа"

            suma_dann = number_to_words(str(suma_chislo))
            print(f'01010 {suma_dann}')

        chislo_propis()

        summa_dog_leas = ''
        suma_dann_dl = ''

        def chislo_propis_dl(vybor_grafic_list):
            nonlocal summa_dog_leas, suma_dann_dl
            book = openpyxl.load_workbook(input_raschet_path, data_only=True)
            sheet = book[vybor_grafic_list]
            summa_dog_leas = sheet['F7'].value

            print(type(f'Сумма дл{summa_dog_leas}'))

            def number_to_words(summa_dog_leas):
                try:
                    # Разбиваем строку на целую и десятичную часть
                    summa_dog_leas = str(round(float(summa_dog_leas), 2)).replace(',', '.') if \
                        str(round(float(summa_dog_leas), 2)).replace(',', '.')[-3] == '.' else str(
                        round(float(summa_dog_leas), 2)).replace(',', '.') + '0'
                    # print(type(summa_dog_leas))
                    parts = summa_dog_leas.split(".")
                    integer_part = parts[0]
                    decimal_part = parts[1] if len(parts) > 1 else "00"

                    # Преобразуем целую часть в число прописью
                    integer_words = num2words(int(integer_part), lang='ru')

                    # Определяем правильную форму для "рублей"
                    if 10 < float(integer_part) % 100 < 20:
                        valute_rub = "рублей"
                    elif float(integer_part) % 10 == 1:
                        valute_rub = "рубль"
                    elif 1 < float(integer_part) % 10 < 5:
                        valute_rub = "рубля"
                    else:
                        valute_rub = "рублей"

                    # Преобразуем десятичную часть в число прописью
                    decimal_words = num2words(int(decimal_part), lang='ru', to='currency', currency='RUB')

                    # Определяем правильную форму для "копеек"
                    if 10 < float(decimal_part) % 100 < 20:
                        valute_copeyka = "копеек"
                    elif float(decimal_part) % 10 == 1:
                        valute_copeyka = "копейка"
                    elif 1 < float(decimal_part) % 10 <= 4:
                        valute_copeyka = "копейки"
                    else:
                        valute_copeyka = "копеек"

                    # Формируем итоговую строку
                    suma_dann_dl = f"{integer_words} {valute_rub} {decimal_words}".strip().replace('ноль рублей',
                                                                                                   '').replace(' ,',
                                                                                                               '')
                    return suma_dann_dl
                except ValueError:
                    return "Неверный формат числа"

            suma_dann_dl = number_to_words(str(summa_dog_leas))

        chislo_propis_dl(grafic)

        if currency_test == 'рублей':
            currency_test = ''
        months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
                  7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}

        old_words = ["{{ a_lkmb }}", "{{ lkmb_podpisant }}", "{{ preambula_dolj_lkmb }}",
                     "{{ preambula_fio_lkmb }}",
                     "{{ deystvuysh }}", "{{ doverka_ustav }}", "{{ full_name_leasee }}",
                     "{{ leader_leasee }}", "{{ fio_leader }}",
                     "{{ doverka_ustav_leasee }}", "{{ inn_seller }}", "{{ vigodo }}", "{{ phone_leasee }}",
                     "{{ email_leasee }}", "{{ full_krakt_name_leasee }}",
                     "{{ address_leasee_expluatazia }}", "{{ investor }}", "{{ r_chet_lkmb }}",
                     "{{ bank_rekv_lkmb }}",
                     "{{ kor_chet_lkmb }}", "{{ bik_lkmb }}",
                     "{{ inn_kpp_leasee }}", "{{ address_leasee }}", "{{ formatted_name_leader_leasee }}",
                     "{{ rekvizit_leasee_bank }}", "{{ rekvizit_leasee_shet }}",
                     "{{ rekvizit_leasee_cs_shet }}", "{{ rekvizit_leasee_bik }}", "{{ deystvuysh_list_leasee }}",
                     "{{ put_padezh_podpisant_rg }}", "{{ leader_leasee_rod_padezh }}", "{{ pl_entry }}",
                     "{{ price_entry }}",
                     "{{ number_dl }}", "{{ currency_test }}", "{{ suma_dann[0] }}", "{{ dt.today().day }}",
                     "{{ months[dt.today().month] }}", "{{ dt.today().year }}", "{{ punkt_4_6 }}",
                     "{{ summa_dog_leas }}", "{{ punkt_7_8 }}", "{{ inn_kpp1 }}", "{{ ogrnip }}",
                     "{{ leader_leasee_pod }}", "{{ imenyemoe }}"]
        # ,
        new_words = [str(a_lkmb), str(lkmb_podpisant), str(preambula_dolj_lkmb), str(preambula_fio_lkmb),
                     str(deystvuysh_list),
                     str(doverka_ustav_list),
                     str(full_name_leasee), str(leader_leasee),
                     str(fio_leader), str(doverka_ustav_leasee), str(inn_seller),
                     str(vigodo), str(phone_leasee), str(email_leasee), str(full_krakt_name_leasee),
                     str(address_leasee_expluatazia),
                     str(investor),
                     str(r_chet_lkmb), str(bank_rekv_lkmb), str(kor_chet_lkmb),
                     str(bik_lkmb), str(inn_kpp_leasee), str(address_leasee), str(formatted_name_leader_leasee),
                     str(rekvizit_leasee_bank),
                     str(rekvizit_leasee_shet), str(rekvizit_leasee_cs_shet),
                     str(rekvizit_leasee_bik), str(deystvuysh_list_leasee),
                     str(put_padezh_podpisant_rg),
                     str(leader_leasee_rod_padezh),
                     str(pl_entry), f'{price_entry:,.2f}'.replace(',', ' ').replace('.', ','), str(number_dl),
                     str(currency_test), str(suma_dann),
                     str(dt.today().day),
                     str(months[dt.today().month]), str(dt.today().year), str(punkt_4_6), str(suma_dann_dl),
                     str(punkt_7_8), str(inn_kpp1), str(ogrnip), str(leader_leasee_pod), str(imenyemoe)]

        # создание ДЛ
        def replace_words_in_docx(docx_file, old_words, new_words):
            doc = Document(docx_file)

            for paragraph in doc.paragraphs:
                for i in range(len(old_words)):
                    if old_words[i] in paragraph.text:
                        paragraph.text = paragraph.text.replace(old_words[i], str(new_words[i]))
                        print(new_words[i])
                        # print(f'_____ {i=}')

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for i in range(len(old_words)):
                            if old_words[i] in cell.text:
                                cell.text = cell.text.replace(old_words[i], new_words[i])
            doc.save(fr"{dir_path}\ДЛ {inn_leasee}.docx")

        def change_font(docx_file, font_name):
            doc = Document(docx_file)

            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    run.font.name = font_name
                    run.font.size = Pt(10)  # Установите желаемый размер шрифта

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.name = font_name
                                run.font.size = Pt(10)  # Установите желаемый размер шрифта

            doc.save(fr"{dir_path}\ДЛ {inn_leasee}.docx")

        if len(inn_leasee) == 12:
            if type_pl != 'on':
                replace_words_in_docx(r"webapp\static\agreement_templates\ШАБЛОН ИП_КФХ.docx", old_words, new_words)
            else:
                replace_words_in_docx(r"webapp\static\agreement_templates\ШАБЛОН ИП_КФХ (обор).docx", old_words,
                                      new_words)
        else:
            if type_pl != 'on':
                replace_words_in_docx(r"webapp\static\agreement_templates\ШАБЛОН ООО_АО.docx", old_words, new_words)
            else:
                replace_words_in_docx(r"webapp\static\agreement_templates\ШАБЛОН ООО_АО (обор).docx", old_words,
                                      new_words)

        change_font(fr"{dir_path}\ДЛ {inn_leasee}.docx", "Times New Roman")

    def grafic_punkty(inn_leasee, path_application, path_graphic, signatory, investor, currency_list, who_is_insure,
                      grafic):

        try:
            book = openpyxl.load_workbook(input_raschet_path, data_only=True)
            sheet = book[grafic]
            # print(f'Тут ГРАФИК {grafic}')
            suma_chislo = sheet['F7'].value
            replacements = {'א': sheet['B9'].value.strftime('%d.%m.%Y'),
                            '{{ B10 }}': sheet['B10'].value.strftime('%d.%m.%Y'),
                            'ב‎': sheet['B11'].value.strftime('%d.%m.%Y'),
                            'גּ‎': sheet['B12'].value.strftime('%d.%m.%Y'),
                            'ג‎': sheet['B13'].value.strftime('%d.%m.%Y'),
                            'דּ‎': sheet['B14'].value.strftime('%d.%m.%Y'),
                            'ד‎': sheet['B15'].value.strftime('%d.%m.%Y'),
                            'ה‎': sheet['B16'].value.strftime('%d.%m.%Y'),
                            'ו‎': sheet['B17'].value.strftime('%d.%m.%Y'),
                            'ז': sheet['B18'].value.strftime('%d.%m.%Y'),
                            'ח': sheet['B19'].value.strftime('%d.%m.%Y'),
                            'ט': sheet['B20'].value.strftime('%d.%m.%Y'),
                            'י': sheet['B21'].value.strftime('%d.%m.%Y'),
                            'כּ': sheet['B22'].value.strftime('%d.%m.%Y'),
                            'כ': sheet['B23'].value.strftime('%d.%m.%Y'),
                            'ךּ': sheet['B24'].value.strftime('%d.%m.%Y'),
                            'ך': sheet['B25'].value.strftime('%d.%m.%Y'),
                            'ל': sheet['B26'].value.strftime('%d.%m.%Y'),
                            'מ': sheet['B27'].value.strftime('%d.%m.%Y'),
                            'ם': sheet['B28'].value.strftime('%d.%m.%Y'),
                            'נ': sheet['B29'].value.strftime('%d.%m.%Y'),
                            'ן': sheet['B30'].value.strftime('%d.%m.%Y'),
                            'ס': sheet['B31'].value.strftime('%d.%m.%Y'),
                            'ע': sheet['B32'].value.strftime('%d.%m.%Y'),
                            'פּ': sheet['B33'].value.strftime('%d.%m.%Y'),
                            'פ': sheet['B34'].value.strftime('%d.%m.%Y'),
                            'ףּ': sheet['B35'].value.strftime('%d.%m.%Y'),
                            'ף': sheet['B36'].value.strftime('%d.%m.%Y'),
                            'צ': sheet['B37'].value.strftime('%d.%m.%Y'),
                            'ץ': sheet['B38'].value.strftime('%d.%m.%Y'),
                            'ק': sheet['B39'].value.strftime('%d.%m.%Y'),
                            'ר': sheet['B40'].value.strftime('%d.%m.%Y'),
                            'שׁ': sheet['B41'].value.strftime('%d.%m.%Y'),
                            'שׂ‎': sheet['B42'].value.strftime('%d.%m.%Y'),
                            'תּ‎': sheet['B43'].value.strftime('%d.%m.%Y'),
                            'ת': sheet['B44'].value.strftime('%d.%m.%Y'),
                            'Ա': sheet['B45'].value.strftime('%d.%m.%Y'),
                            '{{ B46 }}': sheet['B46'].value.strftime('%d.%m.%Y'),
                            'Բ': sheet['B47'].value.strftime('%d.%m.%Y'),
                            'բ': sheet['B48'].value.strftime('%d.%m.%Y'),
                            'Գ': sheet['B49'].value.strftime('%d.%m.%Y'),
                            'գ': sheet['B50'].value.strftime('%d.%m.%Y'),
                            'Դ': sheet['B51'].value.strftime('%d.%m.%Y'),
                            'դ': sheet['B52'].value.strftime('%d.%m.%Y'),
                            'Ե': sheet['B53'].value.strftime('%d.%m.%Y'),
                            'ե': sheet['B54'].value.strftime('%d.%m.%Y'),
                            'Զ': sheet['B55'].value.strftime('%d.%m.%Y'),
                            'զ': sheet['B56'].value.strftime('%d.%m.%Y'),
                            'Է': sheet['B57'].value.strftime('%d.%m.%Y'),
                            'է': sheet['B58'].value.strftime('%d.%m.%Y'),
                            'Ը': sheet['B59'].value.strftime('%d.%m.%Y'),
                            'ը': sheet['B60'].value.strftime('%d.%m.%Y'),
                            'Թ': sheet['B61'].value.strftime('%d.%m.%Y'),
                            'թ': sheet['B62'].value.strftime('%d.%m.%Y'),
                            'Ժ': sheet['B63'].value.strftime('%d.%m.%Y'),
                            'ժ': sheet['B64'].value.strftime('%d.%m.%Y'),
                            'Ի': sheet['B65'].value.strftime('%d.%m.%Y'),
                            'ի': sheet['B66'].value.strftime('%d.%m.%Y'),
                            'ࢱ': sheet['B67'].value.strftime('%d.%m.%Y'),
                            'ࢣ': sheet['B68'].value.strftime('%d.%m.%Y'),
                            'ᵪ': sheet['B93'].value.strftime('%d.%m.%Y'),
                            'Խ': f"{round(float(sheet['F7'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F7'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F7'].value), 2):,}".replace(',', ' ').replace('.',
                                                                                                                    ',') + '0',
                            'Å': f"{round(float(sheet['F8'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F8'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F8'].value), 2):,}".replace(',', ' ').replace('.',
                                                                                                                    ',') + '0',
                            'Ծ': f"{round(float(sheet['F9'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F9'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F9'].value), 2):,}".replace(',', ' ').replace('.',
                                                                                                                    ',') + '0',
                            '{{ F10 }}': f"{round(float(sheet['F10'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F10'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F10'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Կ': f"{round(float(sheet['F11'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F11'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F11'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'կ': f"{round(float(sheet['F12'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F12'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F12'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Հ': f"{round(float(sheet['F13'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F13'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F13'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'հ': f"{round(float(sheet['F14'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F14'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F14'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ձ': f"{round(float(sheet['F15'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F15'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F15'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ձ': f"{round(float(sheet['F16'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F16'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F16'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ղ': f"{round(float(sheet['F17'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F17'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F17'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ղ': f"{round(float(sheet['F18'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F18'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F18'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ճ': f"{round(float(sheet['F19'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F19'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F19'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ճ': f"{round(float(sheet['F20'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F20'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F20'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Մ': f"{round(float(sheet['F21'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F21'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F21'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'մ': f"{round(float(sheet['F22'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F22'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F22'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ո': f"{round(float(sheet['F23'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F23'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F23'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ո': f"{round(float(sheet['F24'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F24'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F24'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'շ': f"{round(float(sheet['F25'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F25'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F25'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Շ': f"{round(float(sheet['F26'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F26'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F26'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ն': f"{round(float(sheet['F27'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F27'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F27'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ն': f"{round(float(sheet['F28'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F28'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F28'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'յ': f"{round(float(sheet['F29'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F29'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F29'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Յ': f"{round(float(sheet['F30'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F30'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F30'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Չ': f"{round(float(sheet['F31'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F31'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F31'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'չ': f"{round(float(sheet['F32'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F32'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F32'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Պ': f"{round(float(sheet['F33'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F33'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F33'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'պ': f"{round(float(sheet['F34'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F34'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F34'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ջ': f"{round(float(sheet['F35'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F35'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F35'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ջ': f"{round(float(sheet['F36'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F36'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F36'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ռ': f"{round(float(sheet['F37'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F37'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F37'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ռ': f"{round(float(sheet['F38'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F38'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F38'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ր': f"{round(float(sheet['F39'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F39'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F39'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ր': f"{round(float(sheet['F40'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F40'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F40'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'տ': f"{round(float(sheet['F41'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F41'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F41'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Տ': f"{round(float(sheet['F42'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F42'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F42'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'վ': f"{round(float(sheet['F43'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F43'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F43'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Վ': f"{round(float(sheet['F44'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F44'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F44'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ս': f"{round(float(sheet['F45'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F45'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F45'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            '{{ F46 }}': f"{round(float(sheet['F46'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F46'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F46'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ց': f"{round(float(sheet['F47'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F47'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F47'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ց': f"{round(float(sheet['F48'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F48'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F48'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ւ': f"{round(float(sheet['F49'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F49'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F49'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ւ': f"{round(float(sheet['F50'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F50'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F50'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Փ': f"{round(float(sheet['F51'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F51'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F51'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'փ': f"{round(float(sheet['F52'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F52'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F52'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ք': f"{round(float(sheet['F53'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F53'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F53'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ք': f"{round(float(sheet['F54'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F54'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F54'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Օ': f"{round(float(sheet['F55'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F55'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F55'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'օ': f"{round(float(sheet['F56'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F56'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F56'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'Ֆ': f"{round(float(sheet['F57'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F57'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F57'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶄ': f"{round(float(sheet['F58'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F58'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F58'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶅ': f"{round(float(sheet['F59'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F59'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F59'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶆ': f"{round(float(sheet['F60'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F60'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F60'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶇ': f"{round(float(sheet['F61'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F61'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F61'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶈ': f"{round(float(sheet['F62'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F62'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F62'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶉ': f"{round(float(sheet['F63'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F63'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F63'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶊ': f"{round(float(sheet['F64'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F64'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F64'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶋ': f"{round(float(sheet['F65'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F65'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F65'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶌ': f"{round(float(sheet['F66'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F66'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F66'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶍ': f"{round(float(sheet['F67'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F67'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F67'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶎ': f"{round(float(sheet['F68'].value), 2):,}".replace(',', ' ').replace('.', ',') if
                            f"{round(float(sheet['F68'].value), 2):,}".replace(',', ' ').replace('.', ',')[
                                -3] == ',' else f"{round(float(sheet['F68'].value), 2):,}".replace(',', ' ').replace(
                                '.', ',') + '0',
                            'ᶏ': f"{round(float(sheet['F93'].value), 2)}".replace('.',
                                                                                  ',') if f"{round(float(sheet['F93'].value), 2)}".replace(
                                '.', ',') == ',' else f"{round(float(sheet['F93'].value), 2)}".replace('.', ',') + '0',
                            }
            # logging.info(replacements)
            # print(replacements)
        except:
            print('Не сработал график')

        doc = docx.Document(fr"{dir_path}\ДЛ {inn_leasee}.docx")
        for para in doc.paragraphs:
            for old_word, new_word in replacements.items():
                for i, run in enumerate(para.runs):
                    if old_word in run.text:
                        # print(old_word, new_word)
                        run.text = run.text.replace(old_word, new_word)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for old_word, new_word in replacements.items():
                        for _ in cell.paragraphs:
                            for o, run in enumerate(_.runs):
                                # print(run.text)
                                if old_word in run.text:
                                    # print(old_word, new_word)
                                    run.text = run.text.replace(old_word, new_word)

        if vikup == '1000':
            for run in doc.paragraphs:
                if run.text == '4.6. Выкупная цена предмета лизинга, равная остаточной стоимости этого предмета лизинга, ' \
                               'рассчитывается в соответствии с действующим законодательством Российской Федерации с ' \
                               'учетом согласованной нормы амортизации. При этом выкупные платежи, уплаченные ' \
                               'Лизингополучателем в составе лизинговых платежей в соответствии с Приложением № 1 к ' \
                               'настоящему договору в качестве выкупных платежей, принимаются в зачет оплаты выкупной ' \
                               'цены предмета лизинга. В случае расторжения настоящего договора по вине ' \
                               'Лизингополучателя, в случае отказа от приемки предмета лизинга уплаченные ' \
                               'Лизингополучателем выкупные платежи возвращению не подлежат, а удерживаются ' \
                               'в качестве штрафа.':
                    doc.element.body.remove(run._element)

        for run in doc.paragraphs:
            if run.text == 'УДАЛИТЬ':
                doc.element.body.remove(run._element)

        if who_is_insure == 'ООО «ЛКМБ-РТ»':
            for run in doc.paragraphs:
                if run.text.strip() in [
                    f'6.1. Лизингополучатель является страхователем в страховой компании, согласованной с Лизингодателем, по страхованию рисков утраты (хищения, угона), ущерба или полной гибели предмета лизинга. Выгодоприобретателем по договору страхования является {vigodo}. Согласованными с Лизингодателем страховыми компаниями являются страховые компании, соответствующие следующим требованиям:',
                    '- наличие действующей лицензии на осуществление страховой деятельности (в т.ч. требуемого вида страхования),',
                    '- осуществление фактической страховой деятельности без отзыва и приостановления лицензии не менее трех лет,',
                    '- имущество страховой компании не находится под арестом,',
                    '- отсутствие негативной информации, которая может поставить под сомнение способность страховой компании качественно и в срок выполнить принятые обязательства (например, уровень выплат по страховым договорам/полисам не менее 40%, и тп.),',
                    '- в отношении страховой компании не ведутся судебные процессы, способные оказать существенное негативное воздействие на ее деятельность, как ограничение, приостановление, либо отзыв лицензии на право осуществления страховой деятельности, вместе с тем, уменьшение стоимости активов страховой компании на 10% (Десять процентов) и более, размера чистой прибыли на 10% (Десять процентов) и более,',
                    '- категория по национальной (российской) рейтинговой шкале финансовой надежности не ниже ВВВ и размещением своих страховых резервов в соответствии с требованиями действующего законодательства Российской Федерации,',
                    '- условия предоставления страховой компанией страховых услуг в полной мере соответствуют требованиям действующего законодательства Российской Федерации,',
                    '- в отношении страховой организации не введена какая-либо из процедур банкротства согласно действующему законодательству, отсутствует решение государственного органа страхового надзора о приостановлении или отзыве лицензии на осуществление страховой деятельности;',
                    '- страховая организация имеет прибыль по результатам страховой деятельности по итогам годовой отчетности за последние два года, предшествующие году рассмотрения о признании страховой компании, отвечающей критериям лизинговой компании;',
                    '- наличие иных факторов, которые прямо или косвенно могут негативно влиять на финансово-экономическое состояние страховой компании;',
                    '- входит в перечень аккредитованных страховых компаний Инвестора.',
                    'Страховая сумма по страхованию на случай утраты (уничтожения, хищения) не может быть менее действительной стоимости предмета лизинга.',
                    'В целях получения разъяснений по условиям страхования Лизингополучатель имеет право обратиться к страховому брокеру Лизингодателя.',
                    f'6.1. Лизингодатель обязуется в течение 10 (Десяти) рабочих дней с даты передачи предмета лизинга по акту приема-передачи застраховать предмет лизинга в страховой компании, выбранной Лизингодателем, от хищения, угона, ущерба и полной гибели имущества на полную стоимость предмета лизинга с момента приема предмета лизинга на срок 12(двенадцать) месяцев. Выгодоприобретателем по договору страхования является {vigodo}.',
                    f'В последующий год и до окончания действия настоящего Договора Лизингополучатель является страхователем в страховой компании, согласованной с Лизингодателем, по страхованию рисков утраты (хищения, угона), ущерба или полной гибели предмета лизинга. Согласованными с Лизингодателем страховыми компаниями являются страховые компании, соответствующие следующим требованиям:']:
                    doc.element.body.remove(run._element)
        elif who_is_insure == '1 год ЛКМБ-РТ, дальше лизингополучатель':
            for run in doc.paragraphs:
                if run.text.strip() in ['6.1. Лизингодатель является страхователем в страховой компании, выбранной ' \
                                        'Лизингодателем, по страхованию рисков утраты (хищения, угона), ' \
                                        'ущерба или полной гибели предмета лизинга. Выгодоприобретателем по ' \
                                        f'договору страхования является {investor if investor != "ПАО «МКБ»" else "ООО «ЛКМБ-РТ»"}.',
                                        '6.1. Лизингодатель является страхователем в страховой компании, выбранной ' \
                                        'Лизингодателем, по страхованию рисков утраты (хищения, угона), ' \
                                        'ущерба или полной гибели предмета лизинга. Выгодоприобретателем по ' \
                                        f'договору страхования является Лизингодатель.',
                                        f'6.1. Лизингополучатель является страхователем в страховой компании, согласованной с Лизингодателем, по страхованию рисков утраты (хищения, угона), ущерба или полной гибели предмета лизинга. Выгодоприобретателем по договору страхования является {vigodo}. Согласованными с Лизингодателем страховыми компаниями являются страховые компании, соответствующие следующим требованиям:']:
                    doc.element.body.remove(run._element)
        else:
            for run in doc.paragraphs:
                if run.text.strip() in [
                    '6.1. Лизингодатель является страхователем в страховой компании, выбранной ' \
                    'Лизингодателем, по страхованию рисков утраты (хищения, угона), ' \
                    'ущерба или полной гибели предмета лизинга. Выгодоприобретателем по ' \
                    f'договору страхования является {investor if investor != "ПАО «МКБ»" else "ООО «ЛКМБ-РТ»"}.',
                    '6.1. Лизингодатель является страхователем в страховой компании, выбранной ' \
                    'Лизингодателем, по страхованию рисков утраты (хищения, угона), ' \
                    'ущерба или полной гибели предмета лизинга. Выгодоприобретателем по ' \
                    f'договору страхования является Лизингодатель.',
                    f'6.1. Лизингодатель обязуется в течение 10 (Десяти) рабочих дней с даты передачи предмета лизинга по акту приема-передачи застраховать предмет лизинга в страховой компании, выбранной Лизингодателем, от хищения, угона, ущерба и полной гибели имущества на полную стоимость предмета лизинга с момента приема предмета лизинга на срок 12(двенадцать) месяцев. Выгодоприобретателем по договору страхования является {vigodo}.',
                    f'В последующий год и до окончания действия настоящего Договора Лизингополучатель является страхователем в страховой компании, согласованной с Лизингодателем, по страхованию рисков утраты (хищения, угона), ущерба или полной гибели предмета лизинга. Согласованными с Лизингодателем страховыми компаниями являются страховые компании, соответствующие следующим требованиям:'
                ]:
                    doc.element.body.remove(run._element)

        if investor == 'ПАО АКБ «МЕТАЛЛИНВЕСТБАНК»'.upper():
            for run in doc.paragraphs:
                if run.text.strip() in ['7.8. Лизингополучатель уведомлен:',
                                        '- о факте передаче предмета лизинга в залог Инвестору в счет исполнения обязательств Лизингодателя (далее в этом пункте также - Заемщик) по Кредитному договору;',
                                        '- о факте заключения договора залога прав требований Заемщика к Лизингополучателю по договору лизинга и передаче указанных прав требования Заемщика к Лизингополучателю в залог Инвестору в счет исполнения обязательств Заемщика по Кредитному договору;',
                                        '- о наличии права Инвестора как залогодержателя по договору залога прав требований Заемщика к Лизингополучателю по договору лизинга осуществить внесудебное обращение взыскания на права требования Заемщика к Лизингополучателю по договору лизинга.',
                                        'В связи с этим Лизингополучатель обязуется:',
                                        '- с даты получения уведомления АО «ПЕРВОУРАЛЬСКБАНК» как залогодержателя прав требований Заемщика к Лизингополучателю по договору лизинга осуществлять исполнения всех без исключения платежных обязательств Лизингополучателя по настоящему договору исключительно в адрес АО «ПЕРВОУРАЛЬСКБАНК» по реквизитам, которые будут указаны в соответствующем уведомлении.',
                                        '- уведомлять АО  «ПЕРВОУРАЛЬСКБАНК» о досрочном или частично досрочном гашении договора лизинга.',
                                        '- что предмет лизинга обременен залогом АО «Инвестторгбанк» по кредитному договору, в рамках которого осуществляется финансирование лизинговой сделки, и что права требования на получение платежей по договору лизинга переданы в залог Банку;',
                                        '- что Лизингополучатель при получении соответствующего уведомления от Банка (залогодержателя) обязан исполнять свое обязательство по договору лизинга Залогодержателю. При этом уведомление направляется любым из способов, определенных договором залога.']:
                    doc.element.body.remove(run._element)
        elif investor == 'АО «ПЕРВОУРАЛЬСКБАНК»'.upper():
            for run in doc.paragraphs:
                if run.text.strip() in [
                    '7.8. Лизингополучатель уведомлен, что предмет залога и залог прав требования '
                    'по настоящему договору переданы в залог ПАО АКБ «МЕТАЛЛИНВЕСТБАНК».',
                    '- что предмет лизинга обременен залогом АО «Инвестторгбанк» по кредитному договору, в рамках которого осуществляется финансирование лизинговой сделки, и что права требования на получение платежей по договору лизинга переданы в залог Банку;',
                    '- что Лизингополучатель при получении соответствующего уведомления от Банка (залогодержателя) обязан исполнять свое обязательство по договору лизинга Залогодержателю. При этом уведомление направляется любым из способов, определенных договором залога.'
                ]:
                    doc.element.body.remove(run._element)
        elif investor == 'АО «Инвестторгбанк»'.upper():
            for run in doc.paragraphs:
                if run.text.strip() in ['7.8. Лизингополучатель уведомлен:',
                                        '- о факте передаче предмета лизинга в залог Инвестору в счет исполнения обязательств Лизингодателя (далее в этом пункте также - Заемщик) по Кредитному договору;',
                                        '- о факте заключения договора залога прав требований Заемщика к Лизингополучателю по договору лизинга и передаче указанных прав требования Заемщика к Лизингополучателю в залог Инвестору в счет исполнения обязательств Заемщика по Кредитному договору;',
                                        '- о наличии права Инвестора как залогодержателя по договору залога прав требований Заемщика к Лизингополучателю по договору лизинга осуществить внесудебное обращение взыскания на права требования Заемщика к Лизингополучателю по договору лизинга.',
                                        'В связи с этим Лизингополучатель обязуется:',
                                        '- с даты получения уведомления АО «ПЕРВОУРАЛЬСКБАНК» как залогодержателя прав требований Заемщика к Лизингополучателю по договору лизинга осуществлять исполнения всех без исключения платежных обязательств Лизингополучателя по настоящему договору исключительно в адрес АО «ПЕРВОУРАЛЬСКБАНК» по реквизитам, которые будут указаны в соответствующем уведомлении.',
                                        '- уведомлять АО  «ПЕРВОУРАЛЬСКБАНК» о досрочном или частично досрочном гашении договора лизинга.',
                                        '7.8. Лизингополучатель уведомлен, что предмет залога и залог прав требования '
                                        'по настоящему договору переданы в залог ПАО АКБ «МЕТАЛЛИНВЕСТБАНК».'
                                        ]:
                    doc.element.body.remove(run._element)
        else:
            for run in doc.paragraphs:
                if run.text.strip() in ['7.8. Лизингополучатель уведомлен:',
                                        '- о факте передаче предмета лизинга в залог Инвестору в счет исполнения обязательств Лизингодателя (далее в этом пункте также - Заемщик) по Кредитному договору;',
                                        '- о факте заключения договора залога прав требований Заемщика к Лизингополучателю по договору лизинга и передаче указанных прав требования Заемщика к Лизингополучателю в залог Инвестору в счет исполнения обязательств Заемщика по Кредитному договору;',
                                        '- о наличии права Инвестора как залогодержателя по договору залога прав требований Заемщика к Лизингополучателю по договору лизинга осуществить внесудебное обращение взыскания на права требования Заемщика к Лизингополучателю по договору лизинга.',
                                        'В связи с этим Лизингополучатель обязуется:',
                                        '- с даты получения уведомления АО «ПЕРВОУРАЛЬСКБАНК» как залогодержателя прав требований Заемщика к Лизингополучателю по договору лизинга осуществлять исполнения всех без исключения платежных обязательств Лизингополучателя по настоящему договору исключительно в адрес АО «ПЕРВОУРАЛЬСКБАНК» по реквизитам, которые будут указаны в соответствующем уведомлении.',
                                        '- уведомлять АО  «ПЕРВОУРАЛЬСКБАНК» о досрочном или частично досрочном гашении договора лизинга.',
                                        '7.8. Лизингополучатель уведомлен, что предмет залога и залог прав требования '
                                        'по настоящему договору переданы в залог ПАО АКБ «МЕТАЛЛИНВЕСТБАНК».',
                                        '- что предмет лизинга обременен залогом АО «Инвестторгбанк» по кредитному договору, в рамках которого осуществляется финансирование лизинговой сделки, и что права требования на получение платежей по договору лизинга переданы в залог Банку;',
                                        '- что Лизингополучатель при получении соответствующего уведомления от Банка (залогодержателя) обязан исполнять свое обязательство по договору лизинга Залогодержателю. При этом уведомление направляется любым из способов, определенных договором залога.'
                                        ]:
                    doc.element.body.remove(run._element)

        doc.save(fr"{dir_path}\ДЛ {inn_leasee}.docx")

    logging.info(f"({current_user}) ЗАПУСК READ XLSX")

    read_xlsx(path_application, pl)  # читает эксель, после этого можно составлять ДЛ

    logging.info(f'({current_user}) ЗАПУСК CREATE DL')
    create_dl_dkp(inn_leasee, path_application, path_graphic, signatory, investor, currency_list, who_is_insure,
                  grafic, pl, number_dl, inn_seller)  # создается ДЛ
    grafic_punkty(inn_leasee, path_application, path_graphic, signatory, investor, currency_list, who_is_insure,
                  grafic)  # заполняет график платежей и убирает ненужные пункты
