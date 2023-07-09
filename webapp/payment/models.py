from webapp.db import db


class Bank(db.Model):
    __tablename__ = "banks"

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String, index=True)
    credit_contracts = db.relationship("CreditContract", backref="bank")

    def __repr__(self):
        return f'Bank {self.id}, {self.bank_name}'


class CreditContract(db.Model):
    __tablename__ = "credit_contracts"

    id = db.Column(db.Integer, primary_key=True)
    credit_contract_name = db.Column(db.String)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'))

    payments = db.relationship("Payment", backref="credit_contract")

    def __repr__(self):
        return f'CreditContract {self.id}, {self.credit_contract_name}'


class LeasingContract(db.Model):
    __tablename__ = 'leasing_contracts'

    id = db.Column(db.Integer, primary_key=True)
    leasing_contract_number = db.Column(db.String, unique=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'))

    payments = db.relationship("Payment", backref="leasing_contract")

    def __repr__(self):
        return f'LeasingContract {self.id}, {self.company_name}'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    leasing_contract_id = db.Column(db.Integer, db.ForeignKey('leasing_contracts.id'))
    date_of_issue = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    credit_contract_id = db.Column(db.Integer, db.ForeignKey('credit_contracts.id'))

    payment_schedules = db.relationship("PaymentSchedule", backref="payment")

    def __repr__(self):
        return f'Payment {self.id}, {self.leasing_contract_id}, {self.date_of_issue}, {self.amount}'


class PaymentSchedule(db.Model):
    __tablename__ = 'payment_schedules'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Float)
    interest_rate = db.Column(db.Float)

    def __repr__(self):
        return f'PaymentSchedule {self.id}, {self.payment_date}, {self.amount}'


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)
    company_inn = db.Column(db.String(20), index=True, unique=True)

    leasing_contracts = db.relationship("LeasingContract", backref="company_name")

    def __repr__(self):
        return f'Company {self.id}, {self.company_name}: {self.company_inn}'


class Seller(db.Model):
    __tablename__ = "sellers"

    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String)
    seller_inn = db.Column(db.String(20), index=True, unique=True)

    leasing_contracts = db.relationship("LeasingContract", backref="seller_name")

    def __repr__(self):
        return f'Seller {self.id}, {self.seller_name}: {self.seller_inn}'
