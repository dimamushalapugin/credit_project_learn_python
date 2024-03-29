from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, login_required, current_user

from webapp.user.forms import LoginForm
from webapp.user.models import User
from webapp.user.views import blueprint as user_blueprint
from webapp.user.auth_utils import admin_required
from webapp.api.views import blueprint as api_blueprint
from webapp.payment.views import blueprint as payment_blueprint
from webapp.risk.views import blueprint as risk_blueprint
from webapp.managers.views import blueprint as manager_blueprint
from webapp.statistics.views import blueprint as statistics_blueprint
from webapp.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "user.login"
    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(payment_blueprint)
    app.register_blueprint(risk_blueprint)
    app.register_blueprint(manager_blueprint)
    app.register_blueprint(statistics_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.route("/")
    @login_required
    def home():
        if current_user.is_manager:
            return redirect(url_for("manager.managers_page"))
        elif current_user.is_risk:
            return redirect(url_for("risk.risk_page"))
        return redirect(url_for("payment.list_of_all_payments"))

    # Обработчик ошибки 404
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.route("/admin")
    @admin_required
    def admin_page():
        users = User.query.all()
        return render_template(
            "admin_profile.html",
            user_name=current_user.fullname,
            user_email=current_user.email,
            user_role=current_user.role,
            user_login=current_user.login,
            user_url=current_user.url_photo,
            user_work_number=current_user.worknumber,
            user_mobile_number=current_user.mobilenumber,
            users=users,
        )

    return app
