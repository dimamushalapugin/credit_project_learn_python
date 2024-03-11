from datetime import datetime

from dateutil.relativedelta import relativedelta
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
from webapp.payment.sql_queries import query_for_info
from webapp.statistics.sql_queries_expert import ExpertRaData
from webapp.user.auth_utils import admin_required
from webapp.risk.logger import logging

blueprint = Blueprint("statistics", __name__, url_prefix="/statistics")


@blueprint.route("/expert-ra-half")
@admin_required
def expert_ra_page_half():
    current_year = datetime.now().year
    return render_template(
        "expert_ra_half.html",
        current_year=current_year,
        expert_ra_6=ExpertRaData(6).get_json(),
    )


@blueprint.route("/expert-ra-nine")
@admin_required
def expert_ra_page_nine():
    current_year = datetime.now().year
    return render_template(
        "expert_ra_nine.html",
        current_year=current_year,
        expert_ra_6=ExpertRaData(9).get_json(),
    )


@blueprint.route("/expert-ra-year")
@admin_required
def expert_ra_page_year():
    current_year = datetime.now().year
    prev_year = current_year - 1
    return render_template(
        "expert_ra_year.html",
        current_year=current_year,
        expert_ra_6=ExpertRaData(12).get_json(),
        prev_year=prev_year,
    )


@blueprint.route("/info-from-base")
@admin_required
def main_info_page():
    return render_template("info_from_base.html", data=query_for_info())
