from flask import render_template, request, Blueprint, redirect, url_for
from flaskblog.models import CompanyData

main = Blueprint('main', __name__)

@main.route("/")
def landing():
    companyData = CompanyData.query.first()
    return render_template('main.html', companydata = companyData)
