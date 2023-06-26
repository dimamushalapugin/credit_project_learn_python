import models
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
from change_xlsx import change_of_date
from sqlalchemy import func
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin

app = Flask(__name__)
app.config.from_pyfile('config.py')
models.db.init_app(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'
#
# class User(models.db.Model, UserMixin):
#     id = models.db.Column(models.db.Integer, primary_key=True)
#     login = models.db.Column(models.db.String(50), nullable=False, unique=True)
#     password = models.db.Column(models.db.String(50), nullable=False)
#     is_active = models.db.Column(models.db.Boolean, default=True)
#
#     def __init__(self, login, password):
#         self.login = login
#         self.password = password
#
# @login_manager.user_loader
# def load_user(user_id):
#     return models.User.query.get(user_id)
# @app.before_request
# def require_login():
#     if request.path != '/login' and not current_user.is_authenticated:
#         return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['inputEmail']
        password = request.form['inputPassword']
        try:
            user = models.User.query.filter(models.User.login == username).first()
        except AttributeError:
            user = None
        try:
            password_check = models.User.query.filter(models.User.password == password).first()
        except AttributeError:
            password_check = None
        if user and password_check and user.password == password:
            login_user(user)
            return redirect(url_for('list_of_all_payments'))
        elif user or password_check:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким логином не найден', 'error')
            return redirect(url_for('login'))
    return render_template('login_page.html')


@app.route('/full_credit_info/<int:leasing_contract_number>', methods=['GET', 'POST'])
@login_required
def full_credit(leasing_contract_number):
    return redirect(url_for('full_credit_info'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/create_new_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        email = request.form['type_pl']
        password = request.form['identificator_pl']
        new_user = models.User(login=email, password=password, blocked=False)
        models.db.session.add(new_user)
        models.db.session.commit()
        return redirect(url_for('list_of_users'))
    return render_template('create_user_page.html')


@app.route('/list_user')
# @login_required
def list_of_users():
    users = models.User.query.all()
    return render_template('users_list.html', users=users)


@app.route('/credit_table')
# @login_required
def list_of_all_payments():
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

    return render_template('credit_table_page.html', result=result)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
# @login_required
def delete_user(user_id):
    user = models.db.session.get(models.User, user_id)
    if user:
        user.delete()
    return redirect(url_for('list_of_users'))


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


@app.route('/total_amount_from_xlsx', methods=['POST'])
# @login_required
def total_amount_from_xlsx():
    df = pd.read_excel(request.files['uploaded_file'])
    return str(df['amount'].sum())


@app.route('/first_page', methods=['GET', 'POST'])
# @login_required
def create_payment():
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


def create_payment_schedule(new_payment):
    df = change_of_date(request.files['uploaded_file'])
    for index, row in df.iterrows():
        new_payment_schedule = models.PaymentSchedule(payment_id=new_payment.id, payment_date=row['payment_date'],
                                                      amount=row['amount'], interest_rate=row['interest_rate'])
        models.db.session.add(new_payment_schedule)
    models.db.session.commit()


@app.route('/')
# @login_required
def home():
    return redirect(url_for('list_of_all_payments'))


if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
    app.run(debug=True)
