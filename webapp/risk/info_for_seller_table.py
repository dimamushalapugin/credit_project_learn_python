import json

from webapp.payment.models import DimaBase
from webapp.risk.logger import logging


def read_pages_for_table(seller_inn, info_first, info_delta, is_factory, is_dealer):
    try:
        info_table = {
            '1. Сведения из ЕГРЮЛ': '',
            'Отсутствуют в реестре данные о контрагенте:': 'Нет',
            'Находится ли контрагент в процессе ликвидации:': info_delta['Процесс ликвидации (да_нет)'],
            'Находится ли контрагент в процессе банкротства:': info_delta['Процесс банкротства (да_нет)'],
            'Находится ли контрагент в процессе реорганизации:': info_delta['Процесс реорганизации (да_нет)'],
            'Имеются ли в реестре отметки о недостоверности сведений:': info_first['Недостоверность сведений (да_нет)'],
            'Различается ли ИНН, ОГРН, адрес, директор, которые указаны в реестре, с теми, что предоставил контрагент:': 'Нет',
            '2. Период деятельности': '',
            'Контрагент ведет деятельность на рынке менее 3 лет:': info_first['Менее 3х лет (да_нет)'],
            '3. Арбитражные дела': '',
            'Имеются ли в отношении контрагента дела, в которых он выступает в качестве ответчика:': info_delta[
                'Ответчик (да_нет)'],
            '4. Сведения о банкротстве': '',
            'У компании имеются сообщения о банкротстве:': info_delta['Сообщения о банкротстве (да_нет)'],
            '5. Исполнительные производства': '',
            'Имеются ли у контрагента исполнительные производства, которые в совокупности превышают 100 тыс. руб.:':
                info_delta['ФССП более 100 (да_нет)'],
            '6. Финансовая отчетность': '',
            'Является ли деятельность контрагента убыточной:': info_first['Убыточность (да_нет)'],
            '7. Адреса массовой регистрации': '',
            'Зарегистрирован ли контрагент по адресу массовой регистрации:': info_first['Массовый адрес (да_нет)'],
            '8. «Массовость» руководителей и участников': '',
            'Является ли директор (учредители) контрагента массовым директором (учредителями):': info_delta[
                'Массовый руководитель (да_нет)'],
            '9. Налоговая задолженность': '',
            'Имеет ли организация превышающую 1000 рублей задолженность по уплате налогов и (или) не предоставляет налоговую отчетность:':
                info_delta['Налоговая задолженность (да_нет)'],
            '10. Заблокированные счета': "",
            'Имеются ли у контрагента заблокированные расчетные счета:': info_delta[
                'Заблокированные расчетные счета (да_нет)'],
            '11. Сведения о причастности к экстремистской деятельности по данным Росфинмониторинг': "",
            'Входит ли контрагент в перечень организаций и физических лиц, в отношении которых имеются сведения об их причастности к экстремистской деятельности или терроризму:':
                info_first['Экстремизм (да_нет)'],
            '12. Черный список ЦБ РФ': '',
            'Контрагент числится в черном списке ЦБ РФ:': 'Нет',
            '13. Государственные контракты': '',
            'У контрагента отсутствуют государственные контракты:': info_delta['Госконтракты (да_нет)'],
            '14. Реестр недобросовестных поставщиков': '',
            'Состоит ли контрагент в реестре недобросовестных поставщиков:': info_delta[
                'Недобросовестный поставщик (да_нет)'],
            '15. Дилерство': '',
            'Поставщик является заводом-изготовителем предмета лизинга:': 'Да' if is_factory == 'on' else 'Нет',
            'Поставщик является официальным дилером завода-изготовителя предмета лизинга:': 'Да' if is_dealer == 'on' else 'Нет',
            '16. Кредитная история в ООО «ЛКМБ-РТ»': '',
            'Имеются (имелись) ли у поставщика договоры купли-продажи с ООО «ЛКМБ-РТ»:': DimaBase.check_in_base(seller_inn)
        }
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        raise Exception('Проблема с таблицей Продавца')

    return info_table


def read_pages_for_table_individual(seller_inn, info_first, is_factory, is_dealer):
    try:
        info_table = {
            '1. Сведения из ЕГРЮЛ': '',
            'Отсутствуют в реестре данные о контрагенте:': 'Нет',
            'Находится ли контрагент в процессе ликвидации:': info_first['Ликвидация (да_нет)'],
            'Находится ли контрагент в процессе банкротства:': info_first['Банкротство (да_нет)'],
            'Находится ли контрагент в процессе реорганизации:': 'Нет',
            'Недостоверности сведений': info_first['Недостоверность сведений (да_нет)'],
            'Различается ли ИНН, ОГРН, адрес, директор, которые указаны в реестре, с теми, что предоставил контрагент:': 'Нет',
            '2. Период деятельности': '',
            'Контрагент ведет деятельность на рынке менее 3 лет:': info_first['Менее 3 лет (да_нет)'],
            '3. Арбитражные дела': '',
            'Имеются ли в отношении контрагента дела, в которых он выступает в качестве ответчика:': info_first['Ответчик (да_нет)'],
            '4. Сведения о банкротстве': '',
            'У компании имеются сообщения о банкротстве:': info_first['Сообщения о банкротстве (да_нет)'],
            '5. Исполнительные производства': '',
            'Имеются ли у контрагента исполнительные производства, которые в совокупности превышают 100 тыс. руб.:': info_first['ФССП более 100 (да_нет)'],
            '6. Финансовая отчетность': '',
            'Является ли деятельность контрагента убыточной:': 'Нет',
            '7. Адреса массовой регистрации': '',
            'Зарегистрирован ли контрагент по адресу массовой регистрации:': info_first['Массовый адрес (да_нет)'],
            '8. «Массовость» руководителей и участников': '',
            'Является ли директор (учредители) контрагента массовым директором (учредителями):': 'Нет',
            '9. Налоговая задолженность': '',
            'Имеет ли организация превышающую 1000 рублей задолженность по уплате налогов и (или) не предоставляет налоговую отчетность:': info_first['Налоговая задолженность (да_нет)'],
            '10. Заблокированные счета': "",
            'Имеются ли у контрагента заблокированные расчетные счета:': info_first['Заблокированные счета (да_нет)'],
            '11. Сведения о причастности к экстремистской деятельности по данным Росфинмониторинг': "",
            'Входит ли контрагент в перечень организаций и физических лиц, в отношении которых имеются сведения об их причастности к экстремистской деятельности или терроризму:': 'Нет',
            '12. Черный список ЦБ РФ': '',
            'Контрагент числится в черном списке ЦБ РФ:': 'Нет',
            '13. Государственные контракты': '',
            'У контрагента отсутствуют государственные контракты:': info_first['Гос контракты (да_нет)'],
            '14. Реестр недобросовестных поставщиков': '',
            'Недобросовестные поставщики': info_first['РНД (да_нет)'],
            '15. Дилерство': '',
            'Поставщик является заводом-изготовителем предмета лизинга:': 'Да' if is_factory == 'on' else 'Нет',
            'Поставщик является официальным дилером завода-изготовителя предмета лизинга:': 'Да' if is_dealer == 'on' else 'Нет',
            '16. Кредитная история в ООО «ЛКМБ-РТ»': '',
            'История в ЛКМБ': DimaBase.check_in_base(seller_inn)
        }
    except Exception as _ex:
        logging.info(_ex, exc_info=True)
        raise Exception('Проблема с таблицей Продавца')

    return info_table
