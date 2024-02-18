import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for, jsonify
from webapp.payment.models import LeasingContract, Payment
from webapp.sql_queries import write_to_db, assign_leasing_contract_id, find_credit_contract_id, \
    create_payment_schedule, query_for_all_payments, query_for_daily_payments, query_for_bank_debts
from webapp.user.auth_utils import admin_required
from webapp.config import DADATA_TOKEN_BKI
from webapp.payment.percent_banks import PeriodDataProcessor

blueprint = Blueprint('payment', __name__, url_prefix='/payments')


@blueprint.route('/full_credit_info/<path:leasing_contract_number>', methods=['GET', 'POST'])
def full_credit_info(leasing_contract_number):
    leasing_contract_number = leasing_contract_number.replace('-', '/')
    lcn = LeasingContract.query.filter(
        LeasingContract.leasing_contract_number == leasing_contract_number).first()
    return render_template('full_credit_page.html', leasing_contract_number=leasing_contract_number)


@blueprint.route('/credit_table')
@admin_required
def list_of_all_payments():
    return render_template('credit_table_page.html', result=query_for_all_payments())


@blueprint.route('/daily_payments')
@admin_required
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
    suggestions_token = DADATA_TOKEN_BKI
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
    return render_template('first_page.html', suggestions_token=suggestions_token)


@blueprint.route('/fill_read_from_xlsx', methods=['GET', 'POST'])
@admin_required
def read_from_xlsx():
    data = request.json.get('data')
    data1 = request.json.get('data1')  # Название банка
    data2 = request.json.get('data2')  # Номер КД
    data3 = request.json.get('data3')  # Размер ставки
    data4 = request.json.get('data4')  # Ставка плав/фикс
    data5 = request.json.get('data5')  # Номер ДЛ
    data6 = request.json.get('data6')  # ИНН лизингополучателя
    data7 = request.json.get('data7')  # ИНН продавца
    data8 = request.json.get('data8')  # Дата выдачи кредита
    file_ = PeriodDataProcessor(data)
    response_math_xlxs = file_.print_output_data()
    json_serializable_data = response_math_xlxs.to_dict(orient='records')
    print(f'Ща будет вывод {data1, data2, data3, data4, data5, data6, data7, data8}')
    return json_serializable_data


@blueprint.route('/writer_read_xlsx', methods=['GET', 'POST'])
@admin_required
def writer_from_xlsx():
    return
