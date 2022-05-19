from flask import render_template, request, Blueprint, redirect, url_for
from flaskblog.models.CompanyData import CompanyData
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def landing():
    companyData = CompanyData.query.first()
    return render_template('main.html', companydata = companyData)
