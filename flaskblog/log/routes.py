from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import CompanyData, Log
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm)


log = Blueprint('log', __name__)

@log.route("/log")
@login_required
def all():
    companyData = CompanyData.query.first()
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('logs.html', logs=logs, companydata = companyData, title='Logs')
