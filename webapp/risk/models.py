from webapp.db import db


class Okved(db.Model):
    __tablename__ = 'okveds'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(), unique=True, index=True)
    name = db.Column(db.String())

    def __repr__(self):
        return f'{self.code} {self.name}'

    @staticmethod
    def return_okved_name(okved_code: str):
        return Okved.query.filter(Okved.code == okved_code).first()




