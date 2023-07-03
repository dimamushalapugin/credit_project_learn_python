from flask import Blueprint, jsonify
from webapp.sql_queries import query_for_daily_payments

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/daily_payments', methods=['GET'])
def get_daily_payments():
    result = query_for_daily_payments()

    payments = []
    for row in result:
        payment_date = row.payment_date.strftime("%d.%m.%Y")

        payment = {
            'payment_date': payment_date,
            'main_debt': row.main_debt,
            'bank_name': row.bank_name
        }
        payments.append(payment)

    return jsonify(payments)
