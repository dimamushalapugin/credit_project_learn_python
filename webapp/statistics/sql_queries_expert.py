import logging
from sqlalchemy import func
from webapp.db import db
from webapp.payment.models import DimaBase
from webapp.payment.sql_queries import format_number


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

    def get_sum_indicator(self, column_name):
        current_year = func.EXTRACT("year", func.CURRENT_DATE())
        if isinstance(self.period, int):
            total_amount = (
                DimaBase.query.with_entities(func.sum(column_name))
                .filter(
                    func.EXTRACT("year", DimaBase.financing_date) == current_year,
                    func.EXTRACT("month", DimaBase.financing_date) <= self.period,
                )
                .scalar()
            )
        else:
            current_period = func.EXTRACT(self.period, func.CURRENT_DATE())
            total_amount = (
                DimaBase.query.with_entities(func.sum(column_name))
                .filter(
                    func.EXTRACT("year", DimaBase.financing_date) == current_year,
                    func.EXTRACT(self.period, DimaBase.financing_date)
                    == current_period,
                )
                .scalar()
            )
        return total_amount

    def get_sum_segment(self, segment):
        current_year = func.EXTRACT("year", func.CURRENT_DATE())
        total_amount = (
            DimaBase.query.with_entities(func.sum(DimaBase.dcp_cost))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= self.period,
                DimaBase.client_segment_type == segment,
            )
            .scalar()
        )
        return total_amount

    def segments_dict(self):
        return {
            "small_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Малый бизнес (численность персонала до 100 чел.; годовая выручка до 800 млн. руб.)"
                        )
                    )
                )
            ),
            "middle_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Средний бизнес (численность персонала 100-250 чел; выручка от 800 млн. до 2 млрд руб.)"
                        )
                    )
                )
            ),
            "large_business": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Крупный бизнес (численность персонала более 250 чел; выручка более 2 млрд руб.)"
                        )
                    )
                )
            ),
            "government": format_number(
                self.with_out_nds(
                    self.million(
                        self.get_sum_segment(
                            "Госучреждения (ФГУП,  МУП,  органы федер. и местной власти и др.)"
                        )
                    )
                )
            ),
            "physical": format_number(
                self.with_out_nds(
                    self.million(self.get_sum_segment("Физические лица (но не ИП)"))
                )
            ),
        }

    def get_count_current_period(self):
        current_year = func.EXTRACT("year", func.CURRENT_DATE())
        if isinstance(self.period, int):
            total_count = (
                DimaBase.query.with_entities(func.count(DimaBase.id))
                .filter(
                    func.EXTRACT("year", DimaBase.financing_date) == current_year,
                    func.EXTRACT("month", DimaBase.financing_date) <= self.period,
                )
                .scalar()
            )
        else:
            current_period = func.EXTRACT(self.period, func.CURRENT_DATE())

            total_count = (
                DimaBase.query.with_entities(func.count(DimaBase.id))
                .filter(
                    func.EXTRACT("year", DimaBase.financing_date) == current_year,
                    func.EXTRACT(self.period, DimaBase.financing_date)
                    == current_period,
                )
                .scalar()
            )
        return total_count

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
            "advance": format_number(
                self.million(self.get_sum_indicator(DimaBase.advance))
            ),
            "co_finance": format_number(
                self.million(self.get_sum_indicator(DimaBase.co_finance))
            ),
            "credit_sum": format_number(
                self.million(self.get_sum_indicator(DimaBase.credit_sum))
            ),
            "client_segment": self.segments_dict(),
        }
