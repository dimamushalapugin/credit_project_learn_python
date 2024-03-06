from webapp.payment.models import InterestRateHistory
from webapp import db, create_app

app = create_app()
with app.app_context():
    interest_rate_history = InterestRateHistory.query.all()
    for row in interest_rate_history:
        print(row.payment_id, row.interest_rate, row.effective_date)
    print(interest_rate_history)
    interest_rate_history_1 = InterestRateHistory.query.filter(
        InterestRateHistory.effective_date <= "2022-10-01"
    ).all()
    print(interest_rate_history_1)
