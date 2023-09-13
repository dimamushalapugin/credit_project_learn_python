import os
from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory, jsonify
from flask_login import login_required

from webapp.managers.parser_for_application import start

blueprint = Blueprint('manager', __name__, url_prefix='/managers')
application_path = ''
graphic_path = ''


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
    return send_from_directory(real_path, filename, as_attachment=True)


def create_docx_file(data):
    return start(data['client_inn'], application_path.replace('/', '\\'), graphic_path.replace('/', '\\'))


@blueprint.route('/create_xlsx', methods=['POST'])
def create_agreement():
    try:
        data = request.form
        file_name = create_docx_file(data)
        flash(f'Файл успешно создан', 'success')
        os.remove(application_path.replace('/', '\\'))
        os.remove(graphic_path.replace('/', '\\'))
        return redirect(url_for('manager.managers_page', file_name=file_name))
    except Exception as e:
        flash(str(e), 'warning')
        os.remove(application_path.replace('/', '\\'))
        os.remove(graphic_path.replace('/', '\\'))
        return redirect(url_for('manager.managers_page'))


@blueprint.route('/upload_files', methods=['POST'])
def upload_files():
    global application_path, graphic_path
    uploaded_application = request.files['uploaded_application']
    uploaded_graphic = request.files['uploaded_graphic']

    if not uploaded_application or not uploaded_graphic:
        return flash('Загрузите оба файла', 'error')

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
