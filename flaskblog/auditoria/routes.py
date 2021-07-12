from flask import render_template, request, Blueprint, send_file
from flaskblog.models import Ciclo
from flaskblog import db

auditoria = Blueprint('auditoria', __name__)

@auditoria.route("/download_cycle_inform/<int:ciclo_id>")
def download_auditoria_inform(ciclo_id):
    path = '/home/jorge/autoclave/flaskblog/static/ciclos/'
    ciclo = Ciclo.query.get_or_404(ciclo_id)
    return send_file(path+ciclo.path,attachment_filename='C21_07_11_20:50.pdf')
