from flask_login import UserMixin
from webapp.db import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(length=50), unique=True)
    password = db.Column(db.String(length=50))
    blocked = db.Column(db.Boolean())
    role = db.Column(db.String(length=50))
    fullname = db.Column(db.String())
    email = db.Column(db.String(length=50))
    url_photo = db.Column(db.String())
    worknumber = db.Column(db.String())
    mobilenumber = db.Column(db.String())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_risk(self):
        return self.role == 'risk'

    @property
    def is_blocked(self):
        return self.blocked is True

    def __repr__(self):
        return f'Пользователь: {self.login}'

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def get_name(self):
        return self.fullname if self.fullname else self.login
