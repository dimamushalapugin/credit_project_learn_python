from webapp.db import db


class Bank(db.Model):
    __tablename__ = "banks"

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String, index=True)
    credit_contracts = db.relationship("CreditContract", backref="bank")

    def __repr__(self):
        return f"Bank {self.id}, {self.bank_name}"


class CreditContract(db.Model):
    __tablename__ = "credit_contracts"

    id = db.Column(db.Integer, primary_key=True)
    credit_contract_name = db.Column(db.String)
    bank_id = db.Column(db.Integer, db.ForeignKey("banks.id"))

    payments = db.relationship("Payment", backref="credit_contract")

    def __repr__(self):
        return f"CreditContract {self.id}, {self.credit_contract_name}"


class LeasingContract(db.Model):
    __tablename__ = "leasing_contracts"

    id = db.Column(db.Integer, primary_key=True)
    leasing_contract_number = db.Column(db.String, unique=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id"))

    payments = db.relationship("Payment", backref="leasing_contract")

    def __repr__(self):
        return f"LeasingContract {self.id}, {self.company_name}"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    leasing_contract_id = db.Column(db.Integer, db.ForeignKey("leasing_contracts.id"))
    date_of_issue = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    floating_or_not = db.Column(db.Boolean)
    credit_contract_id = db.Column(db.Integer, db.ForeignKey("credit_contracts.id"))

    # Отношение с таблицей interest_rate_history
    interest_rate_history = db.relationship("InterestRateHistory", backref="payment")
    payment_schedules = db.relationship("PaymentSchedule", backref="payment")

    def __repr__(self):
        return f"Payment {self.id}, {self.leasing_contract_id}, {self.date_of_issue}, {self.amount}"


class InterestRateHistory(db.Model):
    __tablename__ = "interest_rate_history"

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    interest_rate = db.Column(db.Numeric(precision=10, scale=5), nullable=False)

    # Связь с таблицей payments

    def __repr__(self):
        return f"InterestRateHistory (rate_id={self.payment_id}, interest_rate={self.interest_rate})"


class PaymentSchedule(db.Model):
    __tablename__ = "payment_schedules"

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Float)

    def __repr__(self):
        return f"PaymentSchedule {self.id}, {self.payment_date}, {self.amount}"


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)
    company_inn = db.Column(db.String(20), index=True, unique=True)
    company_ogrn = db.Column(db.String(20), unique=True)
    company_address = db.Column(db.String(100))
    company_reg_date = db.Column(db.Date)

    leasing_contracts = db.relationship("LeasingContract", backref="company_name")

    def __repr__(self):
        return f"Company {self.id}, {self.company_name}: {self.company_inn}"


class Seller(db.Model):
    __tablename__ = "sellers"

    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String)
    seller_inn = db.Column(db.String(20), index=True, unique=True)
    seller_ogrn = db.Column(db.String(20), unique=True)
    seller_address = db.Column(db.String(100))
    seller_reg_date = db.Column(db.Date)

    leasing_contracts = db.relationship("LeasingContract", backref="seller_name")

    def __repr__(self):
        return f"Seller {self.id}, {self.seller_name}: {self.seller_inn}"


class DimaBase(db.Model):
    __tablename__ = "dima_base"

    id = db.Column(db.Integer, primary_key=True)
    schedule = db.Column(db.Text)
    manager = db.Column(db.Text)
    leasing_receiver_name = db.Column(db.Text)
    leasing_receiver_inn = db.Column(db.Text)
    type_start = db.Column(db.Text)
    region = db.Column(db.Text)
    product = db.Column(db.Text)
    client_segment_type = db.Column(db.Text)
    term = db.Column(db.Integer)
    activity_type = db.Column(db.Text)
    product_type = db.Column(db.Text)
    ra_expert = db.Column(db.Text)
    leasing_contract_no = db.Column(db.Text)
    leasing_contract_date = db.Column(db.Date)
    financing_date = db.Column(db.Date)
    contract_amount = db.Column(db.Numeric)
    leasing_object_type = db.Column(db.Text)
    leasing_prev = db.Column(db.Text)
    year_of_leasing_object = db.Column(db.Integer)
    number_of_leasing_objects = db.Column(db.Integer)
    supplier = db.Column(db.Text)
    supplier_inn = db.Column(db.Text, index=True)
    dcp_cost = db.Column(db.Numeric)
    advance = db.Column(db.Numeric)
    credit_sum = db.Column(db.Numeric)
    co_finance = db.Column(db.Numeric)
    total_rate_percentage = db.Column(db.Numeric)
    agent = db.Column(db.Text)
    lkmbrt_margin = db.Column(db.Numeric)
    agent_percentage = db.Column(db.Numeric)

    @staticmethod
    def check_in_base(seller_inn):
        new_seller = DimaBase.query.filter(DimaBase.supplier_inn == seller_inn).first()
        if new_seller:
            return "Да"
        return "Нет"
