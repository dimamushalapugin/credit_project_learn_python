import os
import re
import time

from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory
from flask_login import current_user

from webapp.user.auth_utils import admin_required
from webapp.risk.new_create_risk_conclusion import create_conclusion
from webapp.risk.logger import logging
from webapp.risk.mongo_db import MongoDB

blueprint = Blueprint('risk', __name__, url_prefix='/risk')


def get_folder_names(folder_path):
    folder_names = []
    absolute_folder_path = os.path.join('webapp', folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        folder_names = [item for item in os.listdir(absolute_folder_path) if
                        os.path.isdir(os.path.join(absolute_folder_path, item))]
        folder_names.sort(key=lambda x: os.path.getmtime(os.path.join(absolute_folder_path, x)), reverse=True)

    return folder_names


@blueprint.route('/risk_conclusion')
@admin_required
def risk_page():
    folder_path = 'static/files'
    folder_names = get_folder_names(folder_path)  # Функция для получения списка папок
    return render_template('risk_conclusion.html', folder_names=folder_names)


@blueprint.route('/risk_conclusion/<path:folder_path>')
def risk_conclusion_folder(folder_path):
    base_folder = 'webapp/static/files'
    absolute_folder_path = os.path.join(base_folder, folder_path).replace('\\', '/')

    contents = []

    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        items = os.listdir(absolute_folder_path)
        contents = [{"name": item, "path": os.path.join(folder_path, item).replace('\\', '/')} for item in items]

    return render_template('risk_conclusion_folder.html', folder_path=folder_path, items=contents)


def create_xlsx_file(data):
    pattern = r"^\d{10}$|^\d{12}$"
    if re.match(pattern, data['client_inn']) and re.match(pattern, data['seller_inn']):
        try:
            create_conclusion(data['client_inn'], data['seller_inn'], data.get('factory'), data.get('dealer'))
            return True
        except Exception:
            flash('Вас выбили из Дельты', 'info')
            raise ValueError('Ошибка')
    else:
        flash('Проверьте корректность ИНН.', 'info')
        return False


@blueprint.route('/create_xlsx', methods=['POST'])
def create_risk_conclusion():
    logging.info(f"{current_user} Нажал на кнопку 'Создать риск-заключение'")
    start_time = time.perf_counter()
    try:
        data = request.form
        file_name = create_xlsx_file(data)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(f"({current_user}) Риск-заключение создалось за: {execution_time:.1f} сек.")
        if file_name:
            flash(f'Файл успешно создан', 'success')
            mongo = MongoDB(current_user)
            mongo.write_to_mongodb_risk_count(data['client_inn'], data['seller_inn'])
            return redirect(url_for('risk.risk_page', file_name=file_name))
        else:
            return redirect(url_for('risk.risk_page', file_name=file_name))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('risk.risk_page'))


@blueprint.route('/download/<filename>')
def download(filename):
    folder_path = request.args.get('folder_path')
    real_path = os.path.join('static', 'files', folder_path).replace('\\', '/').replace(f"/{filename}", '')
    logging.info(f"{current_user} скачивает файл: {filename}")
    return send_from_directory(real_path, filename, as_attachment=True)


#  TODO: Найти способ добавить переход на эту страницу после нажати на кнопку создать риск-заключение и не только.
#   Т.е. для ожидания какой либо функции
@blueprint.route('/loading')
def loading():
    return render_template('loading.html')
