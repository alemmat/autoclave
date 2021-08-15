from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db
from flaskblog.models import CompanyData
from flaskblog.companydata.forms import UpdateCompanyDataForm

from flaskblog.companydata.configip import config_ip


companydata = Blueprint('companydata', __name__)

@companydata.route("/companydata", methods=['GET', 'POST'])
@login_required
def company_data():

    form = UpdateCompanyDataForm()
    companyData = CompanyData.query.first()

    if form.validate_on_submit():

        if len( CompanyData.query.all() ) > 0:

            companyData = CompanyData.query.first()
            companyData.companyname = form.companyname.data
            companyData.devicedesignation = form.devicedesignation.data
            companyData.ip = form.ip.data
            db.session.commit()

            config_ip(form.ip.data)

        else:

            companyData = CompanyData(companyname=form.companyname.data, devicedesignation=form.devicedesignation.data, ip=form.ip.data)
            db.session.add(companyData)
            db.session.commit()

            config_ip(form.ip.data)

    elif request.method == 'GET':

        if len( CompanyData.query.all() ) > 0:

            companyData = CompanyData.query.first()
            form.companyname.data = companyData.companyname
            form.devicedesignation.data = companyData.devicedesignation
            form.ip.data = companyData.ip

    return render_template('companydata.html', title='Datos de la empresa', form=form, companydata = companyData)
