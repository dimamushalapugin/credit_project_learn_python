from sqlalchemy import func

from webapp.payment.models import DimaBase


def format_number(number):
    if number is None:
        return "0,00"
    else:
        return "{:,.2f}".format(number).replace(",", " ").replace(".", ",")


def get_sum_indicator(column_name, period):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
    current_month = func.EXTRACT(period, func.CURRENT_DATE())

    total_amount = (
        DimaBase.query.with_entities(func.sum(column_name))
        .filter(
            func.EXTRACT("year", DimaBase.financing_date) == current_year,
            func.EXTRACT(period, DimaBase.financing_date) == current_month,
        )
        .scalar()
    )
    return format_number(total_amount)


def get_count_contracts_per_some_period(period):
    current_year = func.EXTRACT("year", func.CURRENT_DATE())
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


def query_for_monthly_info():
    info_about_lkmb = {
        "month": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "month"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "month"),
            "count_new_contracts": get_count_contracts_per_some_period("month"),
            "advances": get_sum_indicator(DimaBase.advance, "month"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "month"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "month"),
        },
        "quarter": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "quarter"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "quarter"),
            "count_new_contracts": get_count_contracts_per_some_period("quarter"),
            "advances": get_sum_indicator(DimaBase.advance, "quarter"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "quarter"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "quarter"),
        },
        "year": {
            "sum_dl": get_sum_indicator(DimaBase.contract_amount, "year"),
            "sum_dkp": get_sum_indicator(DimaBase.dcp_cost, "year"),
            "count_new_contracts": get_count_contracts_per_some_period("year"),
            "advances": get_sum_indicator(DimaBase.advance, "year"),
            "credit": get_sum_indicator(DimaBase.credit_sum, "year"),
            "co_finance": get_sum_indicator(DimaBase.co_finance, "year"),
        },
    }
    return info_about_lkmb
