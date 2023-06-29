import models
from change_xlsx import change_of_date
from flask import request
from sqlalchemy import func
from datetime import timedelta


def write_to_db(new_data):
    models.db.session.add(new_data)
    models.db.session.commit()


def assign_leasing_contract_id(request_form):
    existing_contract = models.LeasingContract.query.filter(
        models.LeasingContract.leasing_contract_number == request_form).first()

    if existing_contract:
        return existing_contract.id
    else:
        new_leasing_contract = models.LeasingContract(leasing_contract_number=request_form)
        write_to_db(new_leasing_contract)
        return new_leasing_contract.id


def find_credit_contract_id(request_form):
    new_credit_contract = models.CreditContract.query.filter(
        models.CreditContract.credit_contract_name == request_form).first()
    if new_credit_contract:
        return new_credit_contract.id
    return None


def create_payment_schedule(new_payment):
    df = change_of_date(request.files['uploaded_file'])
    for index, row in df.iterrows():
        new_payment_schedule = models.PaymentSchedule(payment_id=new_payment.id, payment_date=row['payment_date'],
                                                      amount=row['amount'], interest_rate=row['interest_rate'])
        models.db.session.add(new_payment_schedule)
    models.db.session.commit()


def query_for_all_payments():
    result = models.db.session.query(
        models.LeasingContract.leasing_contract_number,
        models.Bank.bank_name,
        models.CreditContract.credit_contract_name,
        func.sum(models.PaymentSchedule.amount).label('sum_amount')
    ).select_from(models.PaymentSchedule).join(models.Payment).join(models.LeasingContract).join(
        models.CreditContract).join(models.Bank). \
        filter(models.PaymentSchedule.payment_date > func.CURRENT_DATE()). \
        group_by(
        models.LeasingContract.leasing_contract_number,
        models.Bank.bank_name,
        models.CreditContract.credit_contract_name
    ).all()
    return result


def query_for_daily_payments():
    current_date = func.CURRENT_DATE()
    next_date = current_date + timedelta(days=1)
    date_after_tomorrow = current_date + timedelta(days=2)
    result = models.db.session.query(
        models.PaymentSchedule.payment_date,
        func.sum(models.PaymentSchedule.amount).label('main_debt'),
        models.Bank.bank_name).select_from(models.PaymentSchedule).join(models.Payment).join(
        models.CreditContract).join(models.Bank).filter(
        models.PaymentSchedule.payment_date.in_(
            [current_date, next_date, date_after_tomorrow])).group_by(
        models.PaymentSchedule.payment_date,
        models.Bank.bank_name).all()
    return result
