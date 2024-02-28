import openpyxl
from webapp import db, create_app
from webapp.risk.models import Okved

workbook = openpyxl.load_workbook("okveds.xlsx")
sheet = workbook.active

app = create_app()

with app.app_context():
    for row in sheet.iter_rows(values_only=True):
        code, name = str(row[0]).strip(), row[1].strip()
        existing_seller = Okved.query.filter(Okved.code == code).first()
        if existing_seller:
            continue
        okveds = Okved(code=code, name=name)

        db.session.add(okveds)
    db.session.commit()
