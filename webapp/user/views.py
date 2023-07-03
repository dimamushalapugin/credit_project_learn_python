from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from webapp.user.forms import LoginForm
from webapp.user.models import User
from webapp.db import db
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
@login_required
def create_user():
    if current_user.is_admin:
        if request.method == 'POST':
            login = request.form['type_pl']
            new_user = User(login=login, blocked=False, role='admin')
            new_user.set_password(request.form['identificator_pl'])

            if User.query.filter(User.login == login).count():
                flash('Такой пользователь уже есть')
                return redirect(url_for('user.create_user'))
            write_to_db(new_user)
            return redirect(url_for('user.list_of_users'))
        return render_template('create_user_page.html')
    else:
        return redirect(url_for('payment.list_of_all_payments'))


@blueprint.route('/list_user')
@login_required
def list_of_users():
    if current_user.is_admin:
        users = User.query.all()
        return render_template('users_list.html', users=users)
    else:
        return redirect(url_for('payment.list_of_all_payments'))


@blueprint.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        user.delete()
    return redirect(url_for('user.list_of_users'))
