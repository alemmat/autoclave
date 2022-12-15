from flask import render_template, request, Blueprint, send_file, redirect, url_for, flash, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models import Audit, LineAudit, CompanyData
from flaskblog import db
from sqlalchemy import func, extract
import os
from datetime import datetime, date, time, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

audit = Blueprint('audit', __name__)

path = '/home/pi/autoclave/flaskblog/static/audits/'

@audit.route("/download_audit_inform/<int:audit_id>")
def download_audit_inform(audit_id):
    audit = Audit.query.get_or_404(audit_id)
    if os.path.isfile(path+audit.name):
        return send_file(path+audit.name, attachment_filename=audit.name, as_attachment=True)
    flash('El archivo no existe', 'danger')
    return redirect(url_for('audit.show_all_audit'))

@audit.route("/audit/new")
def new_audit():

    audit = None

    today_query = datetime.utcnow()
    today_audit = Audit.query.filter(
      extract('month', Audit.date_created) >= datetime.today().month,
      extract('year', Audit.date_created) >= datetime.today().year,
      extract('day', Audit.date_created) >= datetime.today().day,
      Audit.state == 0).all()

    if len(today_audit)>0:

        audit  = Audit.query.filter(
          extract('month', Audit.date_created) >= datetime.today().month,
          extract('year', Audit.date_created) >= datetime.today().year,
          extract('day', Audit.date_created) >= datetime.today().day,
          Audit.state == 0).order_by(Audit.date_created.desc()).first()

    else:

        audit = Audit(name="L"+datetime.utcnow().strftime('%y_%m_%d_%H:%M')+".pdf",state=0)
        db.session.add(audit)
        db.session.commit()

    return jsonify( audit_id = audit.id)


@audit.route("/audit/<int:audit_id>/delete", methods=['POST'])
def delete_audit(audit_id):

    audit = Audit.query.get_or_404(audit_id)

    for line in audit.line:
        db.session.delete(line)
        db.session.commit()

    if os.path.isfile(path+audit.name):
        os.remove(path+audit.name)

    db.session.delete(audit)
    db.session.commit()
    return redirect(url_for('audit.show_all_audit'))

@audit.route("/audit")
def show_all_audit():
    companyData = CompanyData.query.first()
    page = request.args.get('page', 1, type=int)
    audits = Audit.query.order_by(Audit.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('audits.html', audits=audits, companydata = companyData)

@audit.route("/audit/<int:audit_id>/insert", methods=['POST'])
def insert_line(audit_id):
    audit = Audit.query.get_or_404(audit_id)
    line_json = request.json
    line = LineAudit(string = line_json["line"],audit_id=audit_id)
    db.session.add(line)
    db.session.commit()
    return "ok"

@audit.route("/audit/close")
def close_audit():
    audits = Audit.query.filter(Audit.date_created <= datetime.now().strftime('%Y-%m-%d'), Audit.state == 0).all()

    return "ok"
