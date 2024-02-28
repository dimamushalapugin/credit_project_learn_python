import os
import re
import time

from pathlib import Path
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
from webapp.config import DADATA_TOKEN_BKI
from webapp.user.auth_utils import risk_required
from webapp.risk.new_create_risk_conclusion import (
    create_conclusion,
    create_conclusion_individual,
)
from webapp.risk.logger import logging
from webapp.risk.mongo_db import MongoDB

blueprint = Blueprint("risk", __name__, url_prefix="/risk")
risk_page_url = "risk.risk_page"


def get_folder_names(folder_path):
    folder_names = []
    absolute_folder_path = os.path.join("webapp", folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        folder_names = [
            item
            for item in os.listdir(absolute_folder_path)
            if os.path.isdir(os.path.join(absolute_folder_path, item))
        ]
        folder_names.sort(
            key=lambda x: os.path.getmtime(os.path.join(absolute_folder_path, x)),
            reverse=True,
        )

    return folder_names


def get_folder_names_individual(folder_path):
    individual_folder_names = []
    absolute_folder_path = os.path.join("webapp", folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        individual_folder_names = [
            item
            for item in os.listdir(absolute_folder_path)
            if os.path.isdir(os.path.join(absolute_folder_path, item))
        ]
        individual_folder_names.sort(
            key=lambda x: os.path.getmtime(os.path.join(absolute_folder_path, x)),
            reverse=True,
        )

    return individual_folder_names


@blueprint.route("/risk_conclusion")
@risk_required
def risk_page():
    folder_path = Path("static") / "files"
    folder_path_individual = Path("static") / "files-individual"
    folder_names = get_folder_names(folder_path)  # Функция для получения списка папок
    individual_folder_names = get_folder_names_individual(
        folder_path_individual
    )  # Функция для получения списка папок физ. лиц
    suggestions_token = DADATA_TOKEN_BKI
    return render_template(
        "risk_conclusion.html",
        folder_names=folder_names,
        individual_folder_names=individual_folder_names,
        suggestions_token=suggestions_token,
    )


@blueprint.route("/risk_conclusion/<path:folder_path>")
def risk_conclusion_folder(folder_path):
    base_folder = Path("webapp") / "static" / "files"
    absolute_folder_path = os.path.join(base_folder, folder_path).replace("\\", "/")

    contents = []

    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        items = os.listdir(absolute_folder_path)
        contents = [
            {"name": item, "path": os.path.join(folder_path, item).replace("\\", "/")}
            for item in items
        ]

    return render_template(
        "risk_conclusion_folder.html", folder_path=folder_path, items=contents
    )


@blueprint.route("/risk-conclusion-individual/<path:folder_path>")
def risk_conclusion_folder_individual(folder_path):
    base_folder = Path("webapp") / "static" / "files-individual"
    absolute_folder_path = os.path.join(base_folder, folder_path).replace("\\", "/")

    contents = []

    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        items = os.listdir(absolute_folder_path)
        contents = [
            {"name": item, "path": os.path.join(folder_path, item).replace("\\", "/")}
            for item in items
        ]

    return render_template(
        "risk_conclusion_folder_individual.html",
        folder_path=folder_path,
        items=contents,
    )


def create_xlsx_file(data):
    pattern = r"^\d{10}$|^\d{12}$"
    if re.match(pattern, data["client_inn"]) and re.match(pattern, data["seller_inn"]):
        try:
            create_conclusion(
                data["client_inn"],
                data["seller_inn"],
                data.get("factory"),
                data.get("dealer"),
            )
            return True
        except Exception:
            flash("Вас выбили из Дельты", "info")
            raise ValueError("Ошибка")
    else:
        flash("Проверьте корректность ИНН.", "info")
        return False


def create_xlsx_file_individual(data):
    try:
        create_conclusion_individual(data)
        return True
    except Exception:
        flash("Вас выбили из Дельты/Ошибка", "info")
        raise ValueError("Ошибка")


@blueprint.route("/create_xlsx", methods=["POST"])
def create_risk_conclusion():
    logging.info(f"{current_user} - Нажал на кнопку 'Создать риск-заключение'")
    start_time = time.perf_counter()
    try:
        data = request.form
        file_name = create_xlsx_file(data)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(
            f"({current_user}) - Риск-заключение создалось за: {execution_time:.1f} сек."
        )
        if file_name:
            flash("Файл успешно создан", "success")
            mongo = MongoDB(current_user)
            mongo.write_to_mongodb_risk_count(data["client_inn"], data["seller_inn"])
            return redirect(url_for(risk_page_url, file_name=file_name))
        else:
            return redirect(url_for(risk_page_url, file_name=file_name))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for(risk_page_url))


@blueprint.route("/create_xlsx_individual", methods=["POST"])
def create_risk_conclusion_individual():
    logging.info(f"{current_user}  - Нажал на кнопку 'Проверка физ. лица'")
    start_time = time.perf_counter()
    try:
        file_name_individual = create_xlsx_file_individual(request.form)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(
            f"({current_user}) Риск-заключение создалось за: {execution_time:.1f} сек."
        )
        if file_name_individual:
            flash("Файл успешно создан", "success")
            return redirect(
                url_for(risk_page_url, file_name_individual=file_name_individual)
            )
        else:
            return redirect(
                url_for(risk_page_url, file_name_individual=file_name_individual)
            )
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for(risk_page_url))


@blueprint.route("/download/<filename>")
def download(filename):
    folder_path = request.args.get("folder_path")
    real_path = (
        os.path.join("static", "files", folder_path)
        .replace("\\", "/")
        .replace(f"/{filename}", "")
    )
    logging.info(f"{current_user} скачивает файл: {filename}")
    return send_from_directory(real_path, filename, as_attachment=True)


@blueprint.route("/download-individual/<filename>")
def download_individual(filename):
    folder_path = request.args.get("folder_path")
    real_path = (
        os.path.join("static", "files-individual", folder_path)
        .replace("\\", "/")
        .replace(f"/{filename}", "")
    )
    logging.info(f"{current_user} путь к файлу: {real_path}")
    logging.info(f"{current_user} скачивает файл: {filename}")
    return send_from_directory(real_path, filename, as_attachment=True)
