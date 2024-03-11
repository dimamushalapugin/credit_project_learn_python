from webapp.payment.models import DimaBase

FILTER_BUSINESS = [
    DimaBase.client_segment_type
    != "Крупный бизнес (численность персонала более 250 чел; выручка более 2 млрд руб.)",
    DimaBase.client_segment_type
    != "Госучреждения (ФГУП,  МУП,  органы федер. и местной власти и др.)",
    DimaBase.client_segment_type != "Физические лица (но не ИП)",
]

FILTER_REGION_MSK = [DimaBase.region == "Москва"]
FILTER_REGION_SPB = [DimaBase.region == "Санкт-Петербург"]
FILTER_REGION_PRIVOLZHSKY = [
    DimaBase.region != "Санкт-Петербург",
    DimaBase.region != "Москва",
]
