from webapp import db, create_app
from webapp.user.models import User
from webapp import config

app = create_app()
with app.app_context():
    user = User(login=config.LOGIN, blocked=False, role='admin')
    user.set_password(config.PASSWORD)
    db.session.add(user)
    db.session.commit()
