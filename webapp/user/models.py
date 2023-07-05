from flask_login import UserMixin
from webapp.db import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    blocked = db.Column(db.Boolean())
    role = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'User {self.id}, {self.login}'

    def delete(self):
        db.session.delete(self)
        db.session.commit()
