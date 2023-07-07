import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from webapp.payment.models import LeasingContract, Payment
from webapp.sql_queries import write_to_db, assign_leasing_contract_id, find_credit_contract_id, \
    create_payment_schedule, query_for_all_payments, query_for_daily_payments, query_for_bank_debts
from webapp.user.auth_utils import admin_required

blueprint = Blueprint('payment', __name__, url_prefix='/payments')


@blueprint.route('/full_credit_info/<path:leasing_contract_number>', methods=['GET', 'POST'])
def full_credit_info(leasing_contract_number):
    leasing_contract_number = leasing_contract_number.replace('-', '/')
    lcn = LeasingContract.query.filter(
        LeasingContract.leasing_contract_number == leasing_contract_number).first()
    return render_template('full_credit_page.html', leasing_contract_number=leasing_contract_number)


@blueprint.route('/credit_table')
@login_required
def list_of_all_payments():
    return render_template('credit_table_page.html', result=query_for_all_payments())


@blueprint.route('/daily_payments')
@login_required
def list_of_daily_payments():
    today_str = datetime.now().strftime('%d.%m.%Y')
    return render_template('daily_payments.html', result=query_for_daily_payments(),
                           bank_debts=query_for_bank_debts(),
                           today_str=today_str)


@blueprint.route('/total_amount_from_xlsx', methods=['POST'])
def total_amount_from_xlsx():
    df = pd.read_excel(request.files['uploaded_file'])
    return str(df['amount'].sum())


@blueprint.route('/first_page', methods=['GET', 'POST'])
@admin_required
def create_payment():
    if request.method == 'POST':
        leasing_contract = assign_leasing_contract_id(request.form['leasing_contract'])
        date_of_issue = datetime.strptime(request.form['date_of_issue'], '%Y-%m-%d').date()
        credit_contract = find_credit_contract_id(request.form['credit_contract'])
        total_amount = float(total_amount_from_xlsx())

        new_payment = Payment(date_of_issue=date_of_issue, leasing_contract_id=leasing_contract,
                              credit_contract_id=credit_contract, total_amount=total_amount)
        write_to_db(new_payment)
        create_payment_schedule(new_payment)
        return redirect(url_for('payment.list_of_all_payments'))
    return render_template('first_page.html')
