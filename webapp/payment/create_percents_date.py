from webapp import db, create_app
from webapp.payment.models import PercentPaymentDate
from webapp.payment.change_xlsx import change_of_date


app = create_app()


df = change_of_date(r"C:\Users\БадриевА\Desktop\Новая папка (2)\% МИБ 5 линия.xlsx")
with app.app_context():
    for index, row in df.iterrows():
        credit_contract_id = row["credit_id"]
        payment_date = row["payment_date"]

        percent_payment_date = PercentPaymentDate(
            credit_contract_id=credit_contract_id, payment_date=payment_date
        )
        db.session.add(percent_payment_date)

    db.session.commit()
