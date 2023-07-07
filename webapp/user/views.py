from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_user, logout_user
from webapp.db import db
from webapp.user.auth_utils import admin_required
from webapp.user.forms import LoginForm
from webapp.user.models import User
from webapp.sql_queries import write_to_db

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login')
def login():
    login_form = LoginForm()
    return render_template('login_page.html', form=login_form)


@blueprint.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Вы вошли на сайт')
            return redirect(url_for('payment.list_of_all_payments'))
    flash('Неправильное имя пользователя или пароль')
    return redirect(url_for('user.login'))


@blueprint.route('/logout')
def exit_user():
    logout_user()
    return redirect(url_for('user.login'))


@blueprint.route('/create_new_user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        login = request.form['user_email']
        new_user = User(login=login, blocked=False, role='admin')
        new_user.set_password(request.form['user_password'])

        if User.query.filter(User.login == login).count():
            flash('Такой пользователь уже есть')
            return redirect(url_for('user.create_user'))
        write_to_db(new_user)
        return redirect(url_for('user.list_of_users'))
    return render_template('create_user_page.html')


@blueprint.route('/list_user')
@admin_required
def list_of_users():
    users = User.query.all()
    return render_template('users_list.html', users=users)


@blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('user.list_of_users'))
