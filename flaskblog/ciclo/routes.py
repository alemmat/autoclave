from flask import render_template, request, Blueprint, send_file, redirect, url_for, flash, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models import Cycle, LineCycle
from flaskblog import db
import os
from datetime import datetime

ciclo = Blueprint('ciclo', __name__)

path = '/home/pi/autoclave/flaskblog/static/ciclos/'

@ciclo.route("/download_cycle_inform/<int:ciclo_id>")
@login_required
def download_cycle_inform(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)
    if os.path.isfile(path+ciclo.name):
        return send_file(path+ciclo.name, attachment_filename=ciclo.name, as_attachment=True)
    flash('El archivo no existe', 'danger')
    return redirect(url_for('ciclo.show_all_ciclo'))


@ciclo.route("/ciclo/<int:ciclo_id>/delete", methods=['POST'])
@login_required
def delete_ciclo(ciclo_id):

    ciclo = Cycle.query.get_or_404(ciclo_id)

    if os.path.isfile(path+ciclo.name):
        os.remove(path+ciclo.name)

    db.session.delete(ciclo)
    db.session.commit()
    return redirect(url_for('ciclo.show_all_ciclo'))

@ciclo.route("/ciclo")
@login_required
def show_all_ciclo():
    page = request.args.get('page', 1, type=int)
    ciclos = Cycle.query.order_by(Cycle.date_created.desc()).paginate(page=page, per_page=5)
    return render_template('ciclos.html', ciclos=ciclos)

@ciclo.route("/ciclo/new")

def new_ciclo():
    ciclo = Cycle(name="C"+datetime.utcnow().strftime('%y_%m_%d_%H:%M')+".pdf",state=0)
    db.session.add(ciclo)
    db.session.commit()
    return jsonify( ciclo_id = ciclo.id)


@ciclo.route("/ciclo/<int:ciclo_id>/insert", methods=['POST'])
def insert_line(ciclo_id):
    ciclo = Cycle.query.get_or_404(ciclo_id)
    line_json = request.json
    line = LineCycle(string = line_json["line"],cycle_id=ciclo_id)
    db.session.add(line)
    db.session.commit()

    for v in ciclo.line:
        print(v.string)

    return "hola"+line_json["line"]
