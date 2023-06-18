import models
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')
models.db.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
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

        return redirect(url_for('list_of_user'))

    return render_template('create_user_page.html')


@app.route('/list_user')
def list_of_user():
    users = models.User.query.all()
    return render_template('users_list.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = models.db.session.get(models.User, user_id)
    if user:
        user.delete()
    return redirect(url_for('list_of_user'))


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
    print(request_form)
    if new_credit_contract:
        return new_credit_contract.id
    return None


@app.route('/first_page', methods=['GET', 'POST'])
def load_xlsx():
    if request.method == 'POST':
        leasing_contract = assign_leasing_contract_id(request.form['leasing_contract'])
        payment_date = datetime.strptime(request.form['payment_date'], '%d.%m.%Y').date()
        credit_contract = find_credit_contract_id(request.form['credit_contract'])

        new_payment = models.Payment(payment_date=payment_date, leasing_contract_id=leasing_contract,
                                     credit_contract_id=credit_contract)
        write_to_db(new_payment)
        return redirect(url_for('success'))
    return render_template('first_page.html')


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('credit_table_page.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    return render_template('credit_table_page.html')


if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
    app.run(debug=True)
