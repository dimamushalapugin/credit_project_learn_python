import models
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime
from sql_queries import write_to_db, assign_leasing_contract_id, find_credit_contract_id, create_payment_schedule, \
    query_for_all_payments, query_for_daily_payments, query_for_bank_debts
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from webapp.forms import LoginForm

app = Flask(__name__)
app.config.from_pyfile('config.py')
models.db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@app.route('/login')
def login():
    title = "Авторизация"
    login_form = LoginForm()
    return render_template('login_page.html', page_title=title, form=login_form)


@app.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(login=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Вы вошли на сайт')
            return redirect(url_for('list_of_all_payments'))
    flash('Неправильное имя пользователя или пароль')
    return redirect(url_for('login'))


@app.route('/full_credit_info/<path:leasing_contract_number>', methods=['GET', 'POST'])
def full_credit_info(leasing_contract_number):
    leasing_contract_number = leasing_contract_number.replace('-', '/')
    lcn = models.LeasingContract.query.filter(
        models.LeasingContract.leasing_contract_number == leasing_contract_number).first()
    return render_template('full_credit_page.html', leasing_contract_number=leasing_contract_number)


@app.route('/logout')
def exit_user():
    logout_user()
    return redirect(url_for('login'))


@app.route('/create_new_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.is_admin:
        if request.method == 'POST':
            login = request.form['type_pl']
            new_user = models.User(login=login, blocked=False, role='admin')
            new_user.set_password(request.form['identificator_pl'])

            if models.User.query.filter(models.User.login == login).count():
                flash('Такой пользователь уже есть')
                return redirect(url_for('create_user'))
            write_to_db(new_user)
            return redirect(url_for('list_of_users'))
        return render_template('create_user_page.html')
    else:
        return redirect(url_for('list_of_all_payments'))


@app.route('/list_user')
@login_required
def list_of_users():
    if current_user.is_admin:
        users = models.User.query.all()
        return render_template('users_list.html', users=users)
    else:
        return redirect(url_for('list_of_all_payments'))


@app.route('/credit_table')
@login_required
def list_of_all_payments():
    return render_template('credit_table_page.html', result=query_for_all_payments())


@app.route('/daily_payments')
@login_required
def list_of_daily_payments():
    today_str = datetime.now().strftime('%d.%m.%Y')
    return render_template('daily_payments.html', result=query_for_daily_payments(), bank_debts=query_for_bank_debts(),
                           today_str=today_str)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = models.db.session.get(models.User, user_id)
    if user:
        user.delete()
    return redirect(url_for('list_of_users'))


@app.route('/total_amount_from_xlsx', methods=['POST'])
def total_amount_from_xlsx():
    df = pd.read_excel(request.files['uploaded_file'])
    return str(df['amount'].sum())


@app.route('/first_page', methods=['GET', 'POST'])
@login_required
def create_payment():
    if current_user.is_admin:
        if request.method == 'POST':
            leasing_contract = assign_leasing_contract_id(request.form['leasing_contract'])
            date_of_issue = datetime.strptime(request.form['date_of_issue'], '%Y-%m-%d').date()
            credit_contract = find_credit_contract_id(request.form['credit_contract'])
            total_amount = float(total_amount_from_xlsx())

            new_payment = models.Payment(date_of_issue=date_of_issue, leasing_contract_id=leasing_contract,
                                         credit_contract_id=credit_contract, total_amount=total_amount)
            write_to_db(new_payment)
            create_payment_schedule(new_payment)
            return redirect(url_for('list_of_all_payments'))
        return render_template('first_page.html')
    else:
        return redirect(url_for('list_of_all_payments'))


@app.route('/')
@login_required
def home():
    return redirect(url_for('list_of_all_payments'))


@app.route('/api/daily_payments', methods=['GET'])
def get_daily_payments():
    result = query_for_daily_payments()

    payments = []
    for row in result:
        payment_date = row.payment_date.strftime("%d.%m.%Y")

        payment = {
            'payment_date': payment_date,
            'main_debt': row.main_debt,
            'bank_name': row.bank_name
        }
        payments.append(payment)

    return jsonify(payments)


if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
    app.run(debug=True)
