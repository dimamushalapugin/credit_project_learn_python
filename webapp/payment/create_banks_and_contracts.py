from webapp import db, create_app
from webapp.payment.models import Bank, CreditContract

app = create_app()
with app.app_context():
    banks = [
        Bank(bank_name="Банк1"),
        Bank(bank_name="Банк2"),
        Bank(bank_name="Банк3"),
        Bank(bank_name="Банк4"),
        Bank(bank_name="Банк5"),
        Bank(bank_name="Банк6"),
        Bank(bank_name="Банк7"),
        Bank(bank_name="Банк8"),
    ]

    contracts = [
        CreditContract(credit_contract_name="Банк1 Договор1", bank=banks[0]),
        CreditContract(credit_contract_name="Банк1 Договор2", bank=banks[0]),
        CreditContract(credit_contract_name="Банк2 Договор1", bank=banks[1]),
        CreditContract(credit_contract_name="Банк2 Договор2", bank=banks[1]),
        CreditContract(credit_contract_name="Банк3 Договор1", bank=banks[2]),
        CreditContract(credit_contract_name="Банк3 Договор2", bank=banks[2]),
        CreditContract(credit_contract_name="Банк3 Договор3", bank=banks[2]),
        CreditContract(credit_contract_name="Банк4 Договор1", bank=banks[3]),
        CreditContract(credit_contract_name="Банк5 Договор1", bank=banks[4]),
        CreditContract(credit_contract_name="Банк5 Договор2", bank=banks[4]),
        CreditContract(credit_contract_name="Банк6 Договор1", bank=banks[5]),
        CreditContract(credit_contract_name="Банк7 Договор1", bank=banks[6]),
        CreditContract(credit_contract_name="Банк8 Договор1", bank=banks[7]),
    ]

    db.session.add_all(banks)
    db.session.add_all(contracts)
    db.session.commit()
