from datetime import timedelta
from flask import request
from sqlalchemy import func
from webapp.db import db
from webapp.payment.change_xlsx import change_of_date
from webapp.payment.models import LeasingContract, Bank, CreditContract, Payment, PaymentSchedule, Company, Seller
from webapp.parsing_egrul import get_customer_name


def write_to_db(new_data):
    db.session.add(new_data)
    db.session.commit()


def assign_leasing_contract_id(request_form):
    existing_contract = LeasingContract.query.filter(
        LeasingContract.leasing_contract_number == request_form).first()
    if existing_contract:
        return existing_contract.id
    else:
        new_leasing_contract = LeasingContract(leasing_contract_number=request_form, company_id=write_company_id(),
                                               seller_id=write_seller_id())
        write_to_db(new_leasing_contract)
        return new_leasing_contract.id


def write_company_id():
    existing_company = Company.query.filter(
        Company.company_inn == request.form['company_inn']).first()
    if not existing_company:
        new_company = Company(company_inn=request.form['company_inn'],
                              company_name=get_customer_name(request.form['company_inn']))
        write_to_db(new_company)
        return new_company.id
    return existing_company.id


def write_seller_id():
    existing_seller = Seller.query.filter(
        Seller.seller_inn == request.form['seller_inn']).first()
    if not existing_seller:
        new_seller = Seller(seller_inn=request.form['seller_inn'],
                            seller_name=get_customer_name(request.form['seller_inn']))
        write_to_db(new_seller)
        return new_seller.id
    return existing_seller.id


def find_credit_contract_id(request_form):
    new_credit_contract = CreditContract.query.filter(
        CreditContract.credit_contract_name == request_form).first()
    if new_credit_contract:
        return new_credit_contract.id
    return None


def create_payment_schedule(new_payment):
    df = change_of_date(request.files['uploaded_file'])
    for index, row in df.iterrows():
        new_payment_schedule = PaymentSchedule(payment_id=new_payment.id, payment_date=row['payment_date'],
                                               amount=row['amount'], interest_rate=row['interest_rate'])
        db.session.add(new_payment_schedule)
    db.session.commit()


def query_for_all_payments():
    result = db.session.query(
        LeasingContract.leasing_contract_number,
        Bank.bank_name,
        CreditContract.credit_contract_name,
        func.sum(PaymentSchedule.amount).label('sum_amount'),
        Company.company_name,
        Company.company_inn
    ).select_from(PaymentSchedule).join(Payment).join(LeasingContract).join(
        CreditContract).join(Bank).join(Company). \
        filter(PaymentSchedule.payment_date > func.CURRENT_DATE()). \
        group_by(
        LeasingContract.leasing_contract_number,
        Bank.bank_name,
        CreditContract.credit_contract_name,
        Company.company_name,
        Company.company_inn
    ).all()
    return result


def query_for_bank_debts():
    bank_debts = db.session.query(
        func.sum(PaymentSchedule.amount).label('payment_amount'),
        Bank.bank_name).select_from(
        PaymentSchedule).join(Payment).join(
        CreditContract).join(Bank).filter(
        PaymentSchedule.payment_date >= func.CURRENT_DATE()).group_by(
        Bank.bank_name).all()
    return bank_debts


def query_for_daily_payments():
    current_date = func.CURRENT_DATE()
    next_date = current_date + timedelta(days=1)
    date_after_tomorrow = current_date + timedelta(days=2)
    result = db.session.query(
        PaymentSchedule.payment_date,
        func.sum(PaymentSchedule.amount).label('main_debt'),
        Bank.bank_name).select_from(PaymentSchedule).join(Payment).join(
        CreditContract).join(Bank).filter(
        PaymentSchedule.payment_date.in_(
            [current_date, next_date, date_after_tomorrow])).group_by(
        PaymentSchedule.payment_date,
        Bank.bank_name).all()
    return result
