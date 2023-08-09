import time

import openpyxl
import os
from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory
from webapp.user.auth_utils import admin_required

blueprint = Blueprint('risk', __name__, url_prefix='/risk')


@blueprint.route('/risk_conclusion', methods=['GET', 'POST'])
@admin_required
def risk_page():
    if request.method == 'GET':
        filenames = os.listdir('webapp/static/files')
        return render_template('risk_conclusion.html', filenames=filenames)

    elif request.method == 'POST':
        folder_path = 'static/files/'
        folders = os.listdir(folder_path)
        data = request.form
        return render_template('risk_conclusion.html', folders=folders, data=data)


def create_xlsx_file(data):
    wb = openpyxl.Workbook()
    ws = wb.active

    ws['A1'] = data['client_inn']
    ws['B1'] = data['seller_inn']

    file_name = 'test.xlsx'
    full_file_path = os.path.join('webapp', 'static', 'files', file_name)
    wb.save(full_file_path)

    return file_name


@blueprint.route('/create_xlsx', methods=['POST'])
def create_xlsx():
    try:
        data = request.form
        time.sleep(2)
        file_name = create_xlsx_file(data)
        flash(f'Файл успешно создан', 'success')
        return redirect(url_for('risk.risk_page', file_name=file_name))
    except Exception as e:
        flash(str(e), 'warning')
        return redirect(url_for('risk.risk_page'))


@blueprint.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(f'static/files/', filename, as_attachment=True)
