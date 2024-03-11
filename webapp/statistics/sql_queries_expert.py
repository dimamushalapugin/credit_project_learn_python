import logging
from sqlalchemy import func
from webapp.payment.models import DimaBase
from webapp.payment.sql_queries import format_number
from webapp.statistics.add_filters import (
    FILTER_BUSINESS,
    FILTER_REGION_MSK,
    FILTER_REGION_SPB,
    FILTER_REGION_PRIVOLZHSKY,
)


class ExpertRa:
    def __init__(self, period):
        self.period = period

    @staticmethod
    def with_out_nds(num):
        if num is None:
            return 0
        else:
            return float(num) / 1.2

    @staticmethod
    def million(num):
        if num is None:
            return 0
        else:
            return num / 1_000_000

    def segments_dict(self):
        return {
            "small_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Малый бизнес (численность персонала до 100 чел.; годовая выручка до 800 млн. руб.)",
                            DimaBase.client_segment_type,
                        )
                    )
                )
            ),
            "middle_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Средний бизнес (численность персонала 100-250 чел; выручка от 800 млн. до 2 млрд руб.)",
                            DimaBase.client_segment_type,
                        )
                    )
                )
            ),
            "large_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Крупный бизнес (численность персонала более 250 чел; выручка более 2 млрд руб.)",
                            DimaBase.client_segment_type,
                        )
                    )
                )
            ),
            "government": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Госучреждения (ФГУП,  МУП,  органы федер. и местной власти и др.)",
                            DimaBase.client_segment_type,
                        )
                    )
                )
            ),
            "physical": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Физические лица (но не ИП)", DimaBase.client_segment_type
                        )
                    )
                )
            ),
        }

    def leasing_subject_dict(self):
        return {
            "new_business": {
                "car": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Легковые автомобили", DimaBase.ra_expert
                            )
                        )
                    )
                ),
                "truck": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Грузовой автотранспорт", DimaBase.ra_expert
                            )
                        )
                    )
                ),
                "bus": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Автобусы и троллейбусы", DimaBase.ra_expert
                            )
                        )
                    )
                ),
                "train": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Железнодорожная техника", DimaBase.ra_expert
                            )
                        )
                    )
                ),
                "air": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Авиационный транспорт", DimaBase.ra_expert
                            )
                        )
                    )
                ),
                "build": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Строительная и дорожно-строительная техника, вкл. Строительную спецтехнику на колесах",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "energy": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Энергетическое оборудование",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "metal": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Машиностроительное, металлообрабатывающее и металлургическое оборудование",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "indust": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для нефте- и газодобычи и переработки",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "agro": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Селькохозяйственная техника и скот",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "tel": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Телекоммуникационное оборудование, оргтехника, компьютеры",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "polygraph": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Полиграфическое оборудование",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "real_estate": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Недвижимость (здания и сооружения)",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "food": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для пищевой промышленности, вкл. Холодильное и оборудование для ресторанов",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "cargo": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Погрузчики складские и складское оборудование, упаковочное оборудование и оборудование для производства тары",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "gkh": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для ЖКХ",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "med": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Медицинская техника и фармацевтическое оборудование",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "water": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Суда (морские и речные)",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "tree": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Деревообрабатывающее оборудование",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
                "other": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Прочее имущество",
                                DimaBase.ra_expert,
                            )
                        )
                    )
                ),
            },
            "new_business_msb": {
                "car": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Легковые автомобили",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "truck": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Грузовой автотранспорт",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "bus": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Автобусы и троллейбусы",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "train": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Железнодорожная техника",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "air": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Авиационный транспорт",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "build": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Строительная и дорожно-строительная техника, вкл. Строительную спецтехнику на колесах",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "energy": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Энергетическое оборудование",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "metal": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Машиностроительное, металлообрабатывающее и металлургическое оборудование",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "indust": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для нефте- и газодобычи и переработки",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "agro": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Селькохозяйственная техника и скот",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "tel": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Телекоммуникационное оборудование, оргтехника, компьютеры",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "polygraph": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Полиграфическое оборудование",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "real_estate": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Недвижимость (здания и сооружения)",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "food": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для пищевой промышленности, вкл. Холодильное и оборудование для ресторанов",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "cargo": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Погрузчики складские и складское оборудование, упаковочное оборудование и оборудование для производства тары",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "gkh": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Оборудование для ЖКХ",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "med": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Медицинская техника и фармацевтическое оборудование",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "water": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Суда (морские и речные)",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "tree": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Деревообрабатывающее оборудование",
                                DimaBase.ra_expert,
                                FILTER_BUSINESS,
                            )
                        )
                    )
                ),
                "other": format_number(
                    self.with_out_nds(
                        self.million(
                            self.get_sum_segment(
                                "Прочее имущество", DimaBase.ra_expert, FILTER_BUSINESS
                            )
                        )
                    )
                ),
            },
        }

    def region_dict(self):
        return {
            "moscow": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_indicator(DimaBase.dcp_cost, FILTER_REGION_MSK)
                    )
                )
            ),
            "spb": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_indicator(DimaBase.dcp_cost, FILTER_REGION_SPB)
                    )
                )
            ),
            "privolzhsky": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_indicator(
                            DimaBase.dcp_cost, FILTER_REGION_PRIVOLZHSKY
                        )
                    )
                )
            ),
        }

    def get_sum_indicator(self, column_name, add_filter: list = []):
        if self.period == 12:
            current_year = func.EXTRACT("year", func.CURRENT_DATE()) - 1
        else:
            current_year = func.EXTRACT("year", func.CURRENT_DATE())
        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= self.period,
                *add_filter,
            )
            .scalar()
        )

        return total_amount

    def get_sum_segment(
        self, segment: str, column_name: DimaBase, add_filter: list = []
    ):
        if self.period == 12:
            current_year = func.EXTRACT("year", func.CURRENT_DATE()) - 1
        else:
            current_year = func.EXTRACT("year", func.CURRENT_DATE())
        total_amount = (
            DimaBase.query.with_entities(func.sum(DimaBase.dcp_cost))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= self.period,
                column_name == segment,
                *add_filter,
            )
            .scalar()
        )

        return total_amount

    def get_count_current_period(self):
        if self.period == 12:
            current_year = func.EXTRACT("year", func.CURRENT_DATE()) - 1
        else:
            current_year = func.EXTRACT("year", func.CURRENT_DATE())
        total_count = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= self.period,
            )
            .scalar()
        )
        return total_count


class ExpertRaData(ExpertRa):
    def __init__(self, period):
        super().__init__(period)

    def get_json(self):
        return {
            "new_business": format_number(
                self.with_out_nds(
                    self.million(self.get_sum_indicator(DimaBase.dcp_cost))
                )
            ),
            "sum_new_business": format_number(
                self.million(self.get_sum_indicator(DimaBase.contract_amount))
            ),
            "new_agreements_count": self.get_count_current_period(),
            "financed_value": format_number(
                self.million(
                    self.get_sum_indicator(DimaBase.credit_sum)
                    + self.get_sum_indicator(DimaBase.co_finance)
                    + self.get_sum_indicator(DimaBase.advance)
                )
            ),
            "financed_structure": {
                "advance": format_number(
                    self.million(self.get_sum_indicator(DimaBase.advance))
                ),
                "co_finance": format_number(
                    self.million(self.get_sum_indicator(DimaBase.co_finance))
                ),
                "credit_sum": format_number(
                    self.million(self.get_sum_indicator(DimaBase.credit_sum))
                ),
                "obligations": format_number(None),
                "other": format_number(None),
            },
            "client_segment": self.segments_dict(),
            "leasing_subject": self.leasing_subject_dict(),
            "region": self.region_dict(),
        }
