from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.testing.pickleable import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty123@localhost:5432/mybase'  # Замените значениями вашей базы данных
db = SQLAlchemy(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login_page.html')

@app.route('/logout')
def exit_user():
    return redirect(url_for('login'))

@app.route('/create_new_user')
def create_user():
    return render_template('create_user_page.html')

@app.route('/list_user')
def list_of_user():
    return render_template('users_list.html')


@app.route('/first_page')
def load_xlsx():
    return render_template('first_page.html')


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('credit_table_page.html')


if __name__ == '__main__':
    app.run(debug=True)
