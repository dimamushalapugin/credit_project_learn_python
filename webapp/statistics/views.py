from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    jsonify,
    url_for,
    send_from_directory,
)
from flask_login import current_user

from webapp.payment.sql_queries import query_for_monthly_info
from webapp.user.auth_utils import admin_required
from webapp.risk.logger import logging

blueprint = Blueprint("statistics", __name__, url_prefix="/statistics")


@blueprint.route("/for-expert-ra")
@admin_required
def expert_ra_page():
    return render_template("expert_ra.html")


@blueprint.route("/info-from-base")
@admin_required
def main_info_page():
    return render_template("info_from_base.html", data=query_for_monthly_info())
