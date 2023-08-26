import os
from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory, jsonify, Response
from webapp.parsing_egrul import get_dir_name, get_customer_name
from webapp.user.auth_utils import admin_required
from webapp.risk.new_create_risk_conclusion import create_conclusion

blueprint = Blueprint('risk', __name__, url_prefix='/risk')


def get_folder_names(folder_path):
    folder_names = []
    absolute_folder_path = os.path.join('webapp', folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        folder_names = [item for item in os.listdir(absolute_folder_path) if
                        os.path.isdir(os.path.join(absolute_folder_path, item))]
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
    return create_conclusion(data['client_inn'], data['seller_inn'])


@blueprint.route('/create_xlsx', methods=['POST'])
def create_risk_conclusion():
    try:
        data = request.form
        file_name = create_xlsx_file(data)
        flash(f'Файл успешно создан', 'success')
        return redirect(url_for('risk.risk_page', file_name=file_name))
    except Exception as e:
        flash(str(e), 'warning')
        return redirect(url_for('risk.risk_page'))


@blueprint.route('/download/<filename>')
def download(filename):
    folder_path = request.args.get('folder_path')
    real_path = os.path.join('static', 'files', folder_path).replace('\\', '/').replace(f"/{filename}", '')
    return send_from_directory(real_path, filename, as_attachment=True)


@blueprint.route('/get_dir_name', methods=['POST'])
def parsing_dir_name(client_inn):
    return get_dir_name(client_inn)
