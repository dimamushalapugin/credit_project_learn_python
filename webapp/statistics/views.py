from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    url_for,
    send_from_directory,
)
from flask_login import current_user
from webapp.risk.logger import logging

blueprint = Blueprint("stat", __name__, url_prefix="/stat")
