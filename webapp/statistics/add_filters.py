from webapp.payment.models import DimaBase

FILTER_BUSINESS = [
    DimaBase.client_segment_type
    == "Малый бизнес (численность персонала до 100 чел.; годовая выручка до 800 млн. руб.)"
    and DimaBase.client_segment_type
    == "Средний бизнес (численность персонала 100-250 чел; выручка от 800 млн. до 2 млрд руб.)"
]

FILTER_REGION_MSK = [DimaBase.region == "Москва"]
FILTER_REGION_SPB = [DimaBase.region == "Санкт-Петербург"]
FILTER_REGION_PRIVOLZHSKY = [
    DimaBase.region != "Санкт-Петербург" or DimaBase.region != "Москва"
]
