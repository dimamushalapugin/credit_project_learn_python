from flask import Flask, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_required, current_user
from flask_caching import Cache

from webapp.user.forms import LoginForm
from webapp.user.models import User
from webapp.user.views import blueprint as user_blueprint
from webapp.api.views import blueprint as api_blueprint
from webapp.payment.views import blueprint as payment_blueprint
from webapp.risk.views import blueprint as risk_blueprint
from webapp.managers.views import blueprint as manager_blueprint
from webapp.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
    cache.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(payment_blueprint)
    app.register_blueprint(risk_blueprint)
    app.register_blueprint(manager_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.route('/')
    @login_required
    def home():
        if current_user.is_manager:
            return redirect(url_for('manager.managers_page'))
        return redirect(url_for('payment.list_of_all_payments'))

    return app
