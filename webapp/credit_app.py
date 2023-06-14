import models
from flask import Flask, render_template, redirect, url_for, request

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
    user = models.User.query.get(user_id)
    if user:
        user.delete()
    return redirect(url_for('list_of_user'))


@app.route('/first_page')
def load_xlsx():
    return render_template('first_page.html')


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('credit_table_page.html')


if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
    app.run(debug=True)
