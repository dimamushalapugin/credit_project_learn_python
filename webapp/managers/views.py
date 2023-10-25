import os

from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory, jsonify, send_file
from flask_login import login_required, current_user

from webapp.managers.parser_for_application import start_filling_application, start_filling_agreement
from webapp.config import APPLICATION_PATH
from webapp.risk.logger import logging

blueprint = Blueprint('manager', __name__, url_prefix='/managers')


#  TODO: Нужно переделать логику кнопки "Предпроверка" в create_agreements.html
def get_folder_names(folder_path):
    folder_names = []
    absolute_folder_path = os.path.join('webapp', folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        folder_names = [item for item in os.listdir(absolute_folder_path) if
                        os.path.isdir(os.path.join(absolute_folder_path, item))]
        folder_names.sort(key=lambda x: os.path.getmtime(os.path.join(absolute_folder_path, x)), reverse=True)

    return folder_names


@blueprint.route('/create_agreements')
@login_required
def managers_page():
    folder_path = 'static/agreements'
    folder_names = get_folder_names(folder_path)  # Функция для получения списка папок
    return render_template('create_agreements.html', folder_names=folder_names)


@blueprint.route('/create_agreements/<path:folder_path>')
def agreements_folder(folder_path):
    base_folder = 'webapp/static/agreements'
    absolute_folder_path = os.path.join(base_folder, folder_path).replace('\\', '/')

    contents = []

    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        items = os.listdir(absolute_folder_path)
        contents = [{"name": item, "path": os.path.join(folder_path, item).replace('\\', '/')} for item in items]

    return render_template('agreements_folder.html', folder_path=folder_path, items=contents)


@blueprint.route('/download/<filename>')
def download(filename):
    folder_path = request.args.get('folder_path')
    real_path = os.path.join('static', 'agreements', folder_path).replace('\\', '/').replace(f"/{filename}", '')
    logging.info(f"{current_user} скачивает файл {filename}'")
    return send_from_directory(real_path, filename, as_attachment=True)


def create_xlsx_file(data):
    return start_filling_application(data['client_inn'], APPLICATION_PATH, data['seller_inn1'], data['seller_inn2'],
                                     data['seller_inn3'], data['seller_inn4'])


def create_docx_file(data, application_path, graphic_path):
    path_application = application_path.replace('/', '\\')
    path_graphic = graphic_path.replace('/', '\\')
    return start_filling_agreement(data['client_inn'], path_application, path_graphic, data['signatory'],
                                   data['investor'], data['currency'], data['insurant'], data['graph'], data['pl'],
                                   data['number_dl'], data['seller_inn'], data['type_pl'])


@blueprint.route('/create_xlsx', methods=['POST'])
def create_agreement():
    logging.info(f"{current_user} Нажал на кнопку 'Создать ДЛ'")
    application_filename = request.form['uploaded_application']
    graphic_filename = request.form['uploaded_graphic']

    application_path = os.path.join('webapp/static/agreement_templates', application_filename)
    graphic_path = os.path.join('webapp/static/agreement_templates', graphic_filename)

    try:
        data = request.form
        file_name = create_docx_file(data, application_path, graphic_path)
        os.remove(application_path.replace('/', '\\'))
        os.remove(graphic_path.replace('/', '\\'))
        logging.info(f"({current_user}) Файлы успешно созданы и загружены")
        flash(f'Файлы успешно созданы и загружены', 'success')
        return redirect(url_for('manager.managers_page', file_name=file_name))
    except Exception as e:
        flash(str(e), 'error')
        os.remove(application_path.replace('/', '\\'))
        os.remove(graphic_path.replace('/', '\\'))
        return redirect(url_for('manager.managers_page'))


@blueprint.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_application = request.files['uploaded_application']
    uploaded_graphic = request.files['uploaded_graphic']

    if not uploaded_application or not uploaded_graphic:
        return flash('Загрузите оба файла', 'info')

    if not (uploaded_application.filename.endswith(('.xlsx', '.xlsm')) and uploaded_graphic.filename.endswith(
            ('.xlsx', '.xlsm'))):
        return flash('Неправильный формат файла. Поддерживаются только .xlsx и .xlsm файлы.', 'error')

    application_filename = uploaded_application.filename
    graphic_filename = uploaded_graphic.filename

    application_path = os.path.join('webapp/static/agreement_templates', application_filename)
    graphic_path = os.path.join('webapp/static/agreement_templates', graphic_filename)

    uploaded_application.save(application_path)
    uploaded_graphic.save(graphic_path)
    return jsonify({'message': 'Файлы успешно загружены и сохранены.'})


@blueprint.route('/download_application')
def download_application(file_path, filename):
    response = send_file(file_path, as_attachment=True, download_name=filename)
    return response


@blueprint.route('/create_application', methods=['POST'])
def create_application():
    logging.info(f"{current_user} Нажал на кнопку 'Создать заявку'")
    try:
        data = request.form
        file_path = create_xlsx_file(data)
        file_name = f'Заявка с заключением {data["client_inn"]}.xlsx'
        flash(f'Файл успешно создан и загружен', 'success')
        return download_application(file_path, file_name)
    except Exception as e:
        flash('Проверьте корректность ИНН', 'error')
        flash('Ошибка:', 'error')
        flash(str(e), 'error')
        return redirect(url_for('manager.managers_page'))
