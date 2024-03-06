import logging

from sqlalchemy import func

from webapp.db import db
from webapp.payment.models import DimaBase


def format_number(number):
    if number is None:
        return "0,00"
    else:
        return "{:,.2f}".format(number).replace(",", " ").replace(".", ",")


def get_sum_indicator(column_name, period):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
    if isinstance(period, int):
        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= period,
            )
            .scalar()
        )
    else:
        current_period = func.EXTRACT(period, func.CURRENT_DATE())
        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT(period, DimaBase.financing_date) == current_period,
            )
            .scalar()
        )
    return format_number(total_amount)


def get_count_current_period(period):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
    if isinstance(period, int):
        total_count = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT("month", DimaBase.financing_date) <= period,
            )
            .scalar()
        )
    else:
        current_period = func.EXTRACT(period, func.CURRENT_DATE())

        total_count = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                func.EXTRACT("year", DimaBase.financing_date) == current_year,
                func.EXTRACT(period, DimaBase.financing_date) == current_period,
            )
            .scalar()
        )
    return total_count


def get_count_for_previous_period(period, interval=0):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
    current_period = func.EXTRACT(period, func.CURRENT_DATE()).label(
        "current_period"
    )  # добавляем ярлык, чтобы можно было обращаться к результату

    if period == "quarter":
        current_quarter_value = db.session.query(current_period).scalar()

        previous_period = current_period - 1 if current_quarter_value != 1 else 4
        previous_year = (
            current_year - 1 if current_quarter_value == 1 else current_year
        ) - interval

        total_amount = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                (
                    (func.EXTRACT("year", DimaBase.financing_date) == current_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == previous_period)
                )
                | (
                    (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == 4)
                )
            )
            .scalar()
        )

    elif period == "month":
        current_month_value = db.session.query(current_period).scalar()
        previous_period = current_period - 1 if current_month_value != 1 else 12
        previous_year = (
            current_year - 1 if current_month_value == 1 else current_year
        ) - interval

        total_amount = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                (
                    (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == previous_period)
                )
            )
            .scalar()
        )
    elif isinstance(period, int):
        previous_year = current_year - 1 - interval
        total_amount = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter(
                (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                & (func.EXTRACT("month", DimaBase.financing_date) <= period)
            )
            .scalar()
        )
    else:
        previous_period = current_year - 1 - interval
        total_amount = (
            DimaBase.query.with_entities(func.count(DimaBase.id))
            .filter((func.EXTRACT(period, DimaBase.financing_date) == previous_period))
            .scalar()
        )

    return total_amount


def get_sum_for_previous_period(column_name, period, interval=0):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
    current_period = func.EXTRACT(period, func.CURRENT_DATE()).label(
        "current_period"
    )  # добавляем ярлык, чтобы можно было обращаться к результату

    if period == "quarter":
        current_quarter_value = db.session.query(current_period).scalar()

        previous_period = current_period - 1 if current_quarter_value != 1 else 4
        previous_year = (
            current_year - 1 if current_quarter_value == 1 else current_year
        ) - interval

        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                (
                    (func.EXTRACT("year", DimaBase.financing_date) == current_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == previous_period)
                )
                | (
                    (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == 4)
                )
            )
            .scalar()
        )

    elif period == "month":
        current_month_value = db.session.query(current_period).scalar()
        previous_period = current_period - 1 if current_month_value != 1 else 12
        previous_year = (
            current_year - 1 if current_month_value == 1 else current_year
        ) - interval

        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                (
                    (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                    & (func.EXTRACT(period, DimaBase.financing_date) == previous_period)
                )
            )
            .scalar()
        )
    elif isinstance(period, int):
        previous_year = current_year - 1 - interval
        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter(
                (func.EXTRACT("year", DimaBase.financing_date) == previous_year)
                & (func.EXTRACT("month", DimaBase.financing_date) <= period)
            )
            .scalar()
        )
    else:
        previous_period = current_year - 1 - interval
        total_amount = (
            DimaBase.query.with_entities(func.sum(column_name))
            .filter((func.EXTRACT(period, DimaBase.financing_date) == previous_period))
            .scalar()
        )

    return format_number(total_amount)


def query_for_info():
    info_about_lkmb = {
        "month": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "month"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "month"),
            "count_new_contracts": get_count_current_period("month"),
            "advances": get_sum_indicator(DimaBase.advance, "month"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "month"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "month"),
        },
        "quarter": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "quarter"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "quarter"),
            "count_new_contracts": get_count_current_period("quarter"),
            "advances": get_sum_indicator(DimaBase.advance, "quarter"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "quarter"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "quarter"),
        },
        "half_year": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, 6),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, 6),
            "count_new_contracts": get_count_current_period(6),
            "advances": get_sum_indicator(DimaBase.advance, 6),
            "credit": get_sum_indicator(DimaBase.credit_sum, 6),
            "co_finance": get_sum_indicator(DimaBase.co_finance, 6),
        },
        "nine_month": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, 9),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, 9),
            "count_new_contracts": get_count_current_period(9),
            "advances": get_sum_indicator(DimaBase.advance, 9),
            "credit": get_sum_indicator(DimaBase.credit_sum, 9),
            "co_finance": get_sum_indicator(DimaBase.co_finance, 9),
        },
        "year": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "year"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "year"),
            "count_new_contracts": get_count_current_period("year"),
            "advances": get_sum_indicator(DimaBase.advance, "year"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "year"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "year"),
        },
        "prev_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "month"),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "month"),
            "count_new_contracts": get_count_for_previous_period("month"),
            "advances": get_sum_for_previous_period(DimaBase.advance, "month"),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "month"),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "month"),
        },
        "prev_quarter": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "quarter"),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "quarter"),
            "count_new_contracts": get_count_for_previous_period("quarter"),
            "advances": get_sum_for_previous_period(DimaBase.advance, "quarter"),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "quarter"),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "quarter"),
        },
        "prev_half_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 6),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 6),
            "count_new_contracts": get_count_for_previous_period(6),
            "advances": get_sum_for_previous_period(DimaBase.advance, 6),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 6),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 6),
        },
        "prev_nine_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 9),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 9),
            "count_new_contracts": get_count_for_previous_period(9),
            "advances": get_sum_for_previous_period(DimaBase.advance, 9),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 9),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 9),
        },
        "prev_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "year"),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "year"),
            "count_new_contracts": get_count_for_previous_period("year"),
            "advances": get_sum_for_previous_period(DimaBase.advance, "year"),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "year"),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "year"),
        },
        "prev_prev_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "month", 1),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "month", 1),
            "count_new_contracts": get_count_for_previous_period("month", 1),
            "advances": get_sum_for_previous_period(DimaBase.advance, "month", 1),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "month", 1),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "month", 1),
        },
        "prev_prev_quarter": {
            "sum_dl": get_sum_for_previous_period(
                DimaBase.contract_amount, "quarter", 1
            ),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "quarter", 1),
            "count_new_contracts": get_count_for_previous_period("quarter", 1),
            "advances": get_sum_for_previous_period(DimaBase.advance, "quarter", 1),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "quarter", 1),
            "co_finance": get_sum_for_previous_period(
                DimaBase.co_finance, "quarter", 1
            ),
        },
        "prev_prev_half_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 6, 1),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 6, 1),
            "count_new_contracts": get_count_for_previous_period(6, 1),
            "advances": get_sum_for_previous_period(DimaBase.advance, 6, 1),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 6, 1),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 6, 1),
        },
        "prev_prev_nine_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 9, 1),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 9, 1),
            "count_new_contracts": get_count_for_previous_period(9, 1),
            "advances": get_sum_for_previous_period(DimaBase.advance, 9, 1),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 9, 1),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 9, 1),
        },
        "prev_prev_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "year", 1),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "year", 1),
            "count_new_contracts": get_count_for_previous_period("year", 1),
            "advances": get_sum_for_previous_period(DimaBase.advance, "year", 1),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "year", 1),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "year", 1),
        },
        "prev_prev_prev_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "month", 2),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "month", 2),
            "count_new_contracts": get_count_for_previous_period("month", 2),
            "advances": get_sum_for_previous_period(DimaBase.advance, "month", 2),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "month", 2),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "month", 2),
        },
        "prev_prev_prev_quarter": {
            "sum_dl": get_sum_for_previous_period(
                DimaBase.contract_amount, "quarter", 2
            ),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "quarter", 2),
            "count_new_contracts": get_count_for_previous_period("quarter", 2),
            "advances": get_sum_for_previous_period(DimaBase.advance, "quarter", 2),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "quarter", 2),
            "co_finance": get_sum_for_previous_period(
                DimaBase.co_finance, "quarter", 2
            ),
        },
        "prev_prev_prev_half_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 6, 2),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 6, 2),
            "count_new_contracts": get_count_for_previous_period(6, 2),
            "advances": get_sum_for_previous_period(DimaBase.advance, 6, 2),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 6, 2),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 6, 2),
        },
        "prev_prev_prev_nine_month": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, 9, 2),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, 9, 2),
            "count_new_contracts": get_count_for_previous_period(9, 2),
            "advances": get_sum_for_previous_period(DimaBase.advance, 9, 2),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, 9, 2),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, 9, 2),
        },
        "prev_prev_prev_year": {
            "sum_dl": get_sum_for_previous_period(DimaBase.contract_amount, "year", 2),
            "sum_dkp": get_sum_for_previous_period(DimaBase.dcp_cost, "year", 2),
            "count_new_contracts": get_count_for_previous_period("year", 2),
            "advances": get_sum_for_previous_period(DimaBase.advance, "year", 2),
            "credit": get_sum_for_previous_period(DimaBase.credit_sum, "year", 2),
            "co_finance": get_sum_for_previous_period(DimaBase.co_finance, "year", 2),
        },
    }
    return info_about_lkmb
