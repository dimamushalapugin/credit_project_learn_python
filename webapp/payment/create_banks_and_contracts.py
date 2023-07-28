from webapp import db, create_app
from webapp.payment.models import Bank, CreditContract

app = create_app()
with app.app_context():
    banks = [
        Bank(bank_name="ПАО «АК БАРС» БАНК"),
        Bank(bank_name="АО «АЛЬФА-БАНК»"),
        Bank(bank_name="АО «КРЕДИТ ЕВРОПА БАНК (РОССИЯ)»"),
        Bank(bank_name="ПАО АКБ «МЕТАЛЛИНВЕСТБАНК»"),
        Bank(bank_name="ПАО «МОСКОВСКИЙ КРЕДИТНЫЙ БАНК»"),
        Bank(bank_name="АО «ПЕРВОУРАЛЬСКБАНК»"),
        Bank(bank_name="АО «СМП БАНК»"),
        Bank(bank_name="АО «СОЛИД БАНК»"),
        Bank(bank_name="АО КБ «УРАЛ ФД»"),
        Bank(bank_name="СОБСТВЕННЫЕ СРЕДСТВА")
    ]

    contracts = [
        CreditContract(credit_contract_name="№ 4502/3/2022/5942 от 22.12.2022", bank=banks[0]),
        CreditContract(credit_contract_name="№ 4502/3/2019/2182 от 13.06.2019", bank=banks[0]),
        CreditContract(credit_contract_name="№ 4502/3/2019/4312 от 08.11.2019", bank=banks[0]),
        CreditContract(credit_contract_name="№ 4502/3/2021/1129 от 06.05.2021", bank=banks[0]),
        CreditContract(credit_contract_name="№ 4502/3/2021/2736 от 11.11.2021", bank=banks[0]),
        CreditContract(credit_contract_name="№ 060Y2L от 26.07.2022", bank=banks[1]),
        CreditContract(credit_contract_name="№ 000001007603 от 01.12.2021", bank=banks[2]),
        CreditContract(credit_contract_name="№ 8365-К от 26.03.2021", bank=banks[3]),
        CreditContract(credit_contract_name="№ 8871-К от 05.10.2021", bank=banks[3]),
        CreditContract(credit_contract_name="№ 9365-К от 06.07.2022", bank=banks[3]),
        CreditContract(credit_contract_name="№ 9847-К от 27.02.2023", bank=banks[3]),
        CreditContract(credit_contract_name="№ 0114/23 от 02.03.2023", bank=banks[4]),
        CreditContract(credit_contract_name="№ 0683/21 от 12.10.2021", bank=banks[4]),
        CreditContract(credit_contract_name="№ 0909/20 от 15.10.2020", bank=banks[4]),
        CreditContract(credit_contract_name="№ 0277/21 от 30.04.2021", bank=banks[4]),
        CreditContract(credit_contract_name="№ ПУБ 130/2022-КД/ЮЛ от 16.05.2022", bank=banks[5]),
        CreditContract(credit_contract_name="№ ПУБ 220/2022-КД/ЮЛ от 27.06.2022", bank=banks[5]),
        CreditContract(credit_contract_name="№ ПУБ 227/2022-КД/ЮЛ от 28.06.2022", bank=banks[5]),
        CreditContract(credit_contract_name="№ ПУБ 777-КД/ЮЛ от 23.09.2021", bank=banks[5]),
        CreditContract(credit_contract_name="№ ПУБ 842-КД/ЮЛ от 26.11.2021", bank=banks[5]),
        CreditContract(credit_contract_name="№ 1400100274.082022КЛ от 04.10.2022", bank=banks[6]),
        CreditContract(credit_contract_name="№ 0504-2021-2010 от 23.08.2021", bank=banks[7]),
        CreditContract(credit_contract_name="№ 0504-2022-2006 от 18.04.2022", bank=banks[7]),
        CreditContract(credit_contract_name="№ 0504-2022-2011 от 25.11.2022", bank=banks[7]),
        CreditContract(credit_contract_name="№ Ю-3994-КЛВ от 08.02.2022", bank=banks[8]),
        CreditContract(credit_contract_name="№ Ю-4043-КЛВ от 08.07.2022", bank=banks[8]),
        CreditContract(credit_contract_name="№ Ю-4179-КЛВ от 31.03.2023", bank=banks[8])
    ]

    db.session.add_all(banks)
    db.session.add_all(contracts)
    db.session.commit()
