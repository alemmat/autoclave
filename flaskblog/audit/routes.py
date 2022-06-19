from flask import render_template, request, Blueprint, send_file, redirect, url_for, flash, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models.Audit import Audit
from flaskblog.models.LineAudit import LineAudit
from flaskblog.models.CompanyData import CompanyData
from flaskblog import db
from sqlalchemy import func, extract
import os
from datetime import datetime, date, time, timedelta
from flaskblog.tasks.GeneratePdf import closeOldAudits

audit = Blueprint('audit', __name__)

path = '/home/jorge/autoclave/flaskblog/static/audits/'

@audit.route("/download_audit_inform/<int:audit_id>")
@login_required
def download_audit_inform(audit_id):
    audit = Audit.query.get_or_404(audit_id)
    if os.path.isfile(path+audit.name):
        return send_file(path+audit.name, attachment_filename=audit.name, as_attachment=True)
    flash('El archivo no existe', 'danger')
    return redirect(url_for('audit.show_all_audit'))

@audit.route("/audit/<int:audit_id>/delete", methods=['POST'])
@login_required
def delete_audit(audit_id):

    audit = Audit.query.get_or_404(audit_id)
    audit.delete()

    return redirect(url_for('audit.show_all_audit'))

@audit.route("/audit")
@login_required
def show_all_audit():
    companyData = CompanyData.query.first()
    page = request.args.get('page', 1, type=int)
    audits = Audit.query.order_by(Audit.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('audits.html', audits=audits, companydata = companyData, title='Auditorias')



@audit.route("/audit/insert", methods=['POST'])
def insert_day_log():

    today = '%'+datetime.now().strftime('%Y-%m-%d')+'%'

    audit = Audit.query.filter(Audit.date_created.like(today)).filter(Audit.state == 0).first()

    if audit is None:

        audit = Audit()

        auditsFromYesterday = Audit.query.filter(Audit.date_created.notlike(today)).filter(Audit.state == 0).all()

        if auditsFromYesterday is not None:

            for auditFromYesterday in auditsFromYesterday:

                auditFromYesterday.genaratePdf()

    audit.insertAuditLine(lineString = request.json["line"])

    return jsonify( audit_id = audit.id)
