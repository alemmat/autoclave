from flask import render_template, request, Blueprint, send_file, redirect, url_for, flash, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models.Cycle import Cycle
from flaskblog.models.LineCycle import LineCycle
from flaskblog.models.CompanyData import CompanyData
from flaskblog import db
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

cycle = Blueprint('cycle', __name__)

path = '/home/jorge/autoclave/flaskblog/static/ciclos/'

@cycle.route("/download_cycle_inform/<int:ciclo_id>")
@login_required
def download_cycle_inform(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)
    if os.path.isfile(path+ciclo.name):
        return send_file(path+ciclo.name, attachment_filename=ciclo.name, as_attachment=True)
    flash('El archivo no existe', 'danger')
    return redirect(url_for('ciclo.show_all_ciclo'))


@cycle.route("/ciclo/<int:ciclo_id>/delete", methods=['POST'])
@login_required
def delete_ciclo(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)
    ciclo.delete()
    return redirect(url_for('ciclo.show_all_ciclo'))

@cycle.route("/ciclo")
@login_required
def show_all_ciclo():
    companyData = CompanyData.query.first()
    page = request.args.get('page', 1, type=int)
    ciclos = Cycle.query.order_by(Cycle.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('ciclos.html', ciclos=ciclos, companydata = companyData, title='Ciclos')

@cycle.route("/ciclo/new")
def new_ciclo():
    ciclo = Cycle()
    return jsonify( ciclo_id = ciclo.id)


@cycle.route("/ciclo/<int:ciclo_id>/insert", methods=['POST'])
def insert_line(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)
    ciclo.insertCycleLine(lineString = request.json["line"])

    return jsonify( ciclo_id = ciclo_id)


@cycle.route("/ciclo/<int:ciclo_id>/close")
def close_cycle(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)
    ciclo.closeCycle()
    return "ok"


@cycle.route("/ciclo/coc")
def close_open_cycle():

    cycles = Cycle.query.filter(Cycle.state == 0).all()

    for cycle in cycles:
        cycle.closeCycleWithError()


    return "ok"
