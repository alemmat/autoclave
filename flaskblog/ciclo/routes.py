from flask import render_template, request, Blueprint, send_file, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.models import Ciclo
from flaskblog import db
import os

ciclo = Blueprint('ciclo', __name__)

path = '/home/pi/autoclave/flaskblog/static/ciclos/'

@ciclo.route("/download_cycle_inform/<int:ciclo_id>")
@login_required
def download_cycle_inform(ciclo_id):

    ciclo = Ciclo.query.get_or_404(ciclo_id)
    if os.path.isfile(path+ciclo.name):
        return send_file(path+ciclo.name, attachment_filename=ciclo.name, as_attachment=True)
    flash('El archivo no existe', 'danger')
    return redirect(url_for('ciclo.show_all_ciclo'))


@ciclo.route("/ciclo/<int:ciclo_id>/delete", methods=['POST'])
@login_required
def delete_ciclo(ciclo_id):

    ciclo = Ciclo.query.get_or_404(ciclo_id)

    if os.path.isfile(path+ciclo.name):
        os.remove(path+ciclo.name)

    db.session.delete(ciclo)
    db.session.commit()
    return redirect(url_for('ciclo.show_all_ciclo'))

@ciclo.route("/ciclo")
@login_required
def show_all_ciclo():
    page = request.args.get('page', 1, type=int)
    ciclos = Ciclo.query.order_by(Ciclo.date_created.desc()).paginate(page=page, per_page=5)
    return render_template('ciclos.html', ciclos=ciclos)
