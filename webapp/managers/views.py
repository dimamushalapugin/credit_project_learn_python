import os
from datetime import date, datetime

from flask import Blueprint, flash, render_template, redirect, request, url_for, send_from_directory, jsonify, send_file
from flask_login import current_user

from webapp.managers.parser_for_application import start_filling_application, start_filling_agreement
from webapp.managers.parser_for_dkp import start_filling_agreement_dkp
from webapp.config import APPLICATION_PATH, DADATA_TOKEN_BKI
from webapp.risk.logger import logging
from webapp.risk.mongo_db import MongoDB
from webapp.managers.parser_for_bki import replace_bki, replace_bki_fiz
from webapp.user.auth_utils import manager_required
from webapp.managers.indiv_bki import FindInd
from webapp.managers.find_gender import Gender

blueprint = Blueprint('manager', __name__, url_prefix='/managers')


def get_folder_names(folder_path):
    folder_names = []
    absolute_folder_path = os.path.join('webapp', folder_path)
    if os.path.exists(absolute_folder_path) and os.path.isdir(absolute_folder_path):
        folder_names = [item for item in os.listdir(absolute_folder_path) if
                        os.path.isdir(os.path.join(absolute_folder_path, item))]
        folder_names.sort(key=lambda x: os.path.getmtime(os.path.join(absolute_folder_path, x)), reverse=True)

    return folder_names


@blueprint.route('/create_agreements')
@manager_required
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
    logging.info(f"({current_user}) скачивает файл {filename}'")
    return send_from_directory(real_path, filename, as_attachment=True)


def create_xlsx_file(data):
    return start_filling_application(data['client_inn'].strip(), APPLICATION_PATH, data['seller_inn1'].strip(),
                                     data['seller_inn2'].strip(), data['seller_inn3'].strip(),
                                     data['seller_inn4'].strip())


def create_docx_file(data, application_path, graphic_path):
    path_application = application_path.replace('/', '\\')
    path_graphic = graphic_path.replace('/', '\\')
    return start_filling_agreement(data['client_inn'].strip(), path_application, path_graphic, data['signatory'],
                                   data['investor'], data['currency'], data['insurant'], data['graph'], data['pl'],
                                   data['number_dl'], data['seller_inn'], data.get('typeSelect'))


def create_docx_file_dkp(data, application_path):
    path_application = application_path.replace('/', '\\')
    return start_filling_agreement_dkp(path_application, data['client_inn'].strip(), data['seller_inn'].strip(),
                                       data['number_dl'], data['signatory'], data['investor'], data['currency'],
                                       data['pl'], data.get('typeSelect'), data['type_pl_new_or_not'],
                                       data['payment_order'], data['place'], data['acts'], data['diadok'],
                                       data.get('pnr'), data.get('house'), data.get('learn'), data.get('stock'))


def create_dl():
    logging.info(f"({current_user}) Нажал на кнопку 'Создать ДЛ'")
    try:
        application_filename = request.form['uploaded_application']
        graphic_filename = request.form['uploaded_graphic']
        application_path = os.path.join('webapp/static/agreement_templates', application_filename)
        graphic_path = os.path.join('webapp/static/agreement_templates', graphic_filename)
    except Exception as ex:
        logging.info(ex, exc_info=True)
        logging.info(f"({current_user}) Ошибка!")
        raise ex

    try:
        data = request.form
        file_name = create_docx_file(data, application_path, graphic_path)
        logging.info(f"({current_user}) Файлы успешно созданы и загружены")
        flash(f'ДЛ успешно создан и загружен', 'success')
        return redirect(url_for('manager.managers_page', file_name=file_name))
    except Exception as ex:
        logging.info(ex, exc_info=True)
        logging.info(f"({current_user}) Ошибка!")
        raise ex


def create_dkp():
    logging.info(f"({current_user}) Нажал на кнопку 'Создать ДКП'")
    try:
        application_filename = request.form['uploaded_application']
        application_path = os.path.join('webapp/static/agreement_templates', application_filename)
    except Exception as ex:
        logging.info(ex, exc_info=True)
        logging.info(f"({current_user}) Ошибка!")
        raise ex

    try:
        data = request.form
        file_name = create_docx_file_dkp(data, application_path)
        logging.info(f"({current_user}) Файлы успешно созданы и загружены")
        flash(f'ДКП успешно создан и загружен', 'success')
        return redirect(url_for('manager.managers_page', file_name=file_name))
    except Exception as ex:
        logging.info(ex, exc_info=True)
        logging.info(f"({current_user}) Ошибка!")
        raise ex


@blueprint.route('/create_xlsx', methods=['POST'])
def create_agreement():
    data = request.form
    logging.info(f"({current_user}) ДЛ - {data.get('check_dl')}, ДКП - {data.get('check_dkp')}")
    try:
        if data.get('check_dl') == 'on':
            application_filename = request.form['uploaded_application']
            graphic_filename = request.form['uploaded_graphic']
            application_path = os.path.join('webapp/static/agreement_templates', application_filename)
            graphic_path = os.path.join('webapp/static/agreement_templates', graphic_filename)
        else:
            application_filename = request.form['uploaded_application']
            application_path = os.path.join('webapp/static/agreement_templates', application_filename)
            graphic_path = None

    except Exception as ex:
        logging.info(ex, exc_info=True)
        flash('Ошибка при получении прикрепленных файлов', 'error')
        return redirect(url_for('manager.managers_page'))

    if data.get('check_dl') == 'on' and data.get('check_dkp') == 'on':
        try:
            create_dl()
            create_dkp()
            return redirect(url_for('manager.managers_page'))
        except Exception as e:
            logging.info(e, exc_info=True)
            flash('Ошибка при создании договора. Проверьте правильность прикрепляемых файлов', 'error')
            return redirect(url_for('manager.managers_page'))
        finally:
            os.remove(application_path.replace('/', '\\'))
            os.remove(graphic_path.replace('/', '\\'))
            return redirect(url_for('manager.managers_page'))

    elif data.get('check_dl') == 'on':
        try:
            create_dl()
            return redirect(url_for('manager.managers_page'))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('manager.managers_page'))
        finally:
            os.remove(application_path.replace('/', '\\'))
            os.remove(graphic_path.replace('/', '\\'))
            return redirect(url_for('manager.managers_page'))
    else:
        try:
            create_dkp()
        except Exception as e:
            flash(str(e), 'error')
        finally:
            os.remove(application_path.replace('/', '\\'))

    return redirect(url_for('manager.managers_page'))


@blueprint.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_application = request.files['uploaded_application']
    uploaded_graphic = request.files.get('uploaded_graphic')

    if uploaded_graphic is not None:
        if not (uploaded_application.filename.endswith(('.xlsx', '.xlsm')) and uploaded_graphic.filename.endswith(
                ('.xlsx', '.xlsm'))):
            return flash('Неправильный формат файла. Поддерживаются только .xlsx и .xlsm файлы.', 'error')
    else:
        if not uploaded_application.filename.endswith(('.xlsx', '.xlsm')):
            return flash('Неправильный формат файла. Поддерживаются только .xlsx и .xlsm файлы.', 'error')

    application_filename = uploaded_application.filename
    if uploaded_graphic is not None:
        graphic_filename = uploaded_graphic.filename
    else:
        graphic_filename = None

    application_path = os.path.join('webapp/static/agreement_templates', application_filename)
    if uploaded_graphic is not None:
        graphic_path = os.path.join('webapp/static/agreement_templates', graphic_filename)
    else:
        graphic_path = None

    uploaded_application.save(application_path)

    if uploaded_graphic is not None:
        uploaded_graphic.save(graphic_path)

    return jsonify({'message': 'Файлы успешно загружены и сохранены.'})


@blueprint.route('/download_application')
def download_application(file_path, filename):
    # print(f"Attempting to download file: {file_path}/{filename}")
    response = send_file(file_path, as_attachment=True, download_name=filename)
    return response


@blueprint.route('/create_application', methods=['POST'])
def create_application():
    logging.info(f"({current_user}) Нажал на кнопку 'Создать заявку'")
    try:
        data = request.form
        mongo = MongoDB(current_user)
        mongo.write_to_mongodb_app_count(data["client_inn"].strip(), data["seller_inn1"].strip(),
                                         data["seller_inn2"].strip(), data["seller_inn3"].strip(),
                                         data["seller_inn4"].strip())
        file_path = create_xlsx_file(data)
        file_name = f'Заявка с заключением {data["client_inn"].strip()}.xlsx'
        return download_application(file_path, file_name)
    except Exception as e:
        flash('Проверьте корректность ИНН', 'error')
        flash('Ошибка:', 'error')
        flash(str(e), 'error')
        return redirect(url_for('manager.managers_page'))


@blueprint.route('/create_bki')
@manager_required
def bki_page():
    suggestions_token = DADATA_TOKEN_BKI
    return render_template('create_bki.html', suggestions_token=suggestions_token)


#  TODO: нужно ввести доп. проверку по длине ИНН в поле БКИ для юр. лиц.
#   Чтобы сразу выводило ошибку, что ИП/КФХ нужно вводить в форму для физ. лиц
@blueprint.route('/check_inn', methods=['POST'])
def check_inn():
    mongo = MongoDB(current_user)
    inn = request.form.get('inn')
    try:
        dir_name = Gender(request.form.get('director_name', '')).get_name
    except Exception as ex:
        logging.info(ex, exc_info=True)
        dir_name = request.form.get('director_name', '')
    dir_post = request.form.get('director_position', '').capitalize()
    # Здесь выполняется проверка наличия информации об ИНН в вашей БД
    company_details = mongo.read_mongodb_company_bki(inn)
    today = date.today().strftime("%Y-%m-%d")
    if company_details:
        company_name = company_details.get('company_name', '')
        company_ogrn = company_details.get('company_ogrn', '')
        company_address = company_details.get('company_address', '')
        signatory_name = company_details.get('signatory_name', '')
        signatory_position = company_details.get('signatory_position', '')
        signatory_basis = company_details.get('signatory_basis', '')
        company_phone = company_details.get('company_phone', '')
        return jsonify({
            'company_name': company_name,
            'company_inn': inn,
            'company_ogrn': company_ogrn,
            'company_address': company_address,
            'signatory_name': signatory_name,
            'signatory_position': signatory_position,
            'signatory_basis': signatory_basis,
            'company_phone': company_phone,
            'today': today
        })
    else:
        # Если информация не найдена
        return jsonify({'today': today, 'dir_name': dir_name, 'dir_post': dir_post})


@blueprint.route('/check_inn_indiv', methods=['POST'])
def check_inn_indiv():
    mongo = MongoDB(current_user)
    inn = request.form.get('inn')
    director_details = mongo.read_mongodb_director_details(inn)
    today = date.today().strftime("%Y-%m-%d")
    if director_details:
        director_name = director_details.get('director_name', '')
        try:
            date_of_birth = director_details.get('date_of_birth').split()[0]
        except IndexError:
            date_of_birth = director_details.get('date_of_birth', '')
        place_of_birth = director_details.get('place_of_birth', '')
        passport_series = director_details.get('passport_series', '')
        passport_id = director_details.get('passport_id', '')
        issued_by = director_details.get('issued_by', '')
        try:
            issued_when = director_details.get('issued_when').split()[0]
        except IndexError:
            issued_when = director_details.get('issued_when', '')
        department_code = director_details.get('department_code', '')
        address_reg = director_details.get('address_reg', '')
        return jsonify({
            'director_name': director_name,
            'director_inn': inn,
            'date_of_birth': date_of_birth,
            'place_of_birth': place_of_birth,
            'passport_series': passport_series,
            'passport_id': passport_id,
            'issued_by': issued_by,
            'issued_when': issued_when,
            'department_code': department_code,
            'address_reg': address_reg,
            'today': today
        })
    else:
        director_name = FindInd(inn).get_fio
        return jsonify({'today': today, 'director_name': director_name, 'director_inn': inn})


@blueprint.route('/autofillfiz', methods=['POST'])
def autofillfiz():
    mongo = MongoDB(current_user)
    data = request.form['data'].strip()
    director_details = mongo.read_mongodb_director_details(data)
    if director_details:
        autofilled_data = director_details.get('director_name', '')
        try:
            autofilled_data7 = director_details.get('date_of_birth').split()[0]
        except IndexError:
            autofilled_data7 = director_details.get('date_of_birth', '')
        autofilled_data6 = director_details.get('place_of_birth', '')
        autofilled_data1 = director_details.get('passport_series', '')
        autofilled_data2 = director_details.get('passport_id', '')
        autofilled_data3 = director_details.get('issued_by', '')
        try:
            autofilled_data4 = director_details.get('issued_when').split()[0]
        except IndexError:
            autofilled_data4 = director_details.get('issued_when', '')
        autofilled_data5 = director_details.get('department_code', '')
        autofilled_data8 = director_details.get('address_reg', '')
    else:
        person = FindInd(data)
        autofilled_data = person.get_fio
        autofilled_data1 = ''
        autofilled_data2 = ''
        autofilled_data3 = ''
        autofilled_data4 = ''
        autofilled_data5 = ''
        autofilled_data6 = ''
        autofilled_data7 = ''
        autofilled_data8 = ''
    current_date = date.today()
    autofilled_data9 = current_date.strftime("%Y-%m-%d")
    return jsonify({'data1': autofilled_data, 'data2': autofilled_data1, 'data3': autofilled_data2,
                    'data4': autofilled_data3, 'data5': autofilled_data4, 'data6': autofilled_data5,
                    'data7': autofilled_data6, 'data8': autofilled_data7, 'data9': autofilled_data8,
                    'data10': autofilled_data9})


@blueprint.route('/submit_form_ur', methods=['POST'])
def submit_form_ur():
    # data = request.form['data']
    data_inn_ur = request.form['data']
    data_naming_ur = request.form['data1']
    data_ogrn_ur = request.form['data2']
    data_address_ur = request.form['data3']
    data_phone_ur = request.form['data4']
    data_fio_ur = request.form['data5']
    data_leader_ur = request.form['data6']
    data_doverka_ur = request.form['data7']
    data_year_ur = request.form['data8']
    mongo = MongoDB(current_user)
    data = {
        'company_name': request.form['data1'].strip(),
        'company_inn': request.form['data'].strip(),
        'company_ogrn': request.form['data2'].strip(),
        'company_address': request.form['data3'].strip(),
        'company_phone': request.form['data4'].strip(),
        'signatory_name': request.form['data5'].strip(),
        'signatory_position': request.form['data6'].strip(),
        'signatory_basis': request.form['data7'].strip(),
        'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
    }
    mongo.write_to_mongodb_company_bki(data)
    replace_bki(data_inn_ur, data_naming_ur, data_ogrn_ur, data_address_ur, data_phone_ur, data_fio_ur, data_leader_ur,
                data_doverka_ur, data_year_ur)

    return redirect(url_for('manager.bki_page'))


@blueprint.route('/submit_form_fiz', methods=['POST'])
def submit_form_fiz():
    data_inn_fiz = request.form['data'].strip()
    data_naming_fiz = request.form['data1'].strip()
    data_ser_fiz = request.form['data2'].strip()
    data_numb_fiz = request.form['data3'].strip()
    data_whoismvd_fiz = request.form['data4'].strip()
    data_output_fiz = request.form['data5'].strip()
    data_code_fiz = request.form['data6'].strip()
    data_birthplace_fiz = request.form['data7'].strip()
    data_birthdate_fiz = request.form['data8']
    data_address_fiz = request.form['data9'].strip()
    data_year_fiz = request.form['data10']
    mongo = MongoDB(current_user)
    data = {
        'director_name': data_naming_fiz,
        'director_inn': data_inn_fiz,
        'date_of_birth': data_birthdate_fiz,
        'place_of_birth': data_birthplace_fiz,
        'passport_id': data_numb_fiz,
        'passport_series': data_ser_fiz,
        'issued_by': data_whoismvd_fiz,
        'issued_when': data_output_fiz,
        'department_code': data_code_fiz,
        'address_reg': data_address_fiz,
        'address_fact': data_address_fiz,
        'date': datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
    }
    mongo.write_to_mongodb_individual_bki(data)
    replace_bki_fiz(data_inn_fiz, data_naming_fiz, data_ser_fiz, data_numb_fiz, data_whoismvd_fiz, data_output_fiz,
                    data_code_fiz,
                    data_birthplace_fiz, data_birthdate_fiz, data_address_fiz, data_year_fiz)
    return jsonify(data_naming_fiz)


@blueprint.route('/process', methods=['POST'])
def process_file():
    inn = 'Тут должен быть ИНН'
    return render_template('create_agreements.html', inn=inn)
