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
        }
