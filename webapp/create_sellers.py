import openpyxl
from webapp import db, create_app
from webapp.payment.models import Seller

workbook = openpyxl.load_workbook('sellers.xlsx')
sheet = workbook.active

app = create_app()

with app.app_context():
    for row in sheet.iter_rows(values_only=True):
        seller_name, seller_inn = row[0].strip().upper(), str(row[1]).strip()
        existing_seller = Seller.query.filter(Seller.seller_inn == seller_inn).first()
        if existing_seller:
            continue
        seller = Seller(seller_name=seller_name, seller_inn=seller_inn)

        db.session.add(seller)
    db.session.commit()
