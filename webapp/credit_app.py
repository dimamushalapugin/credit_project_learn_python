import models
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from datetime import datetime
import pandas as pd
from flask_login import LoginManager, login_user, login_required

app = Flask(__name__)
app.config.from_pyfile('config.py')
models.db.init_app(app)
app.config['SECRET_KEY'] = '12134587481321321'

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['inputEmail']
        password = request.form['inputPassword']
        print(username, password)
        try:
            user = models.User.query.filter(models.User.login == username).first().login
        except AttributeError:
            user = None
        try:
            password_check = models.User.query.filter(models.User.password == password).first().password
        except AttributeError:
            password_check = None
        print("user:", user)
        print("password_check:", password_check)
        if user == username and password_check == password:
            return redirect(url_for('home'))
        elif user != username or password_check != password:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    return render_template('login_page.html')


@app.route('/logout')
def exit_user():
    return redirect(url_for('login'))


@app.route('/create_new_user', methods=['GET', 'POST'])
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
def list_of_users():
    users = models.User.query.all()
    return render_template('users_list.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = models.db.session.get(models.User, user_id)
    if user:
        user.delete()
    return redirect(url_for('list_of_users'))


def write_to_db(new_data):
    models.db.session.add(new_data)
    models.db.session.commit()


def assign_leasing_contract_id(request_form):
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
def total_amount_from_xlsx():
    df = pd.read_excel(request.files['uploaded_file'])
    return str(df['amount'].sum())


@app.route('/first_page', methods=['GET', 'POST'])
def create_payment():
    if request.method == 'POST':
        leasing_contract = assign_leasing_contract_id(request.form['leasing_contract'])
        payment_date = datetime.strptime(request.form['payment_date'], '%d.%m.%Y').date()
        credit_contract = find_credit_contract_id(request.form['credit_contract'])
        amount = float(total_amount_from_xlsx())

        new_payment = models.Payment(payment_date=payment_date, leasing_contract_id=leasing_contract,
                                     credit_contract_id=credit_contract, amount=amount)
        write_to_db(new_payment)
        create_payment_schedule(new_payment)

        return redirect(url_for('home'))
    return render_template('first_page.html')


def create_payment_schedule(new_payment):
    df = pd.read_excel(request.files['uploaded_file'])
    for index, row in df.iterrows():
        new_payment_schedule = models.PaymentSchedule(payment_id=new_payment.id, payment_date=row['payment_date'],
                                                      amount=row['amount'], interest_rate=row['interest_rate'])
        models.db.session.add(new_payment_schedule)
    models.db.session.commit()


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('credit_table_page.html')


if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
    app.run(debug=True)
