from flask import render_template, request, Blueprint, send_file
from flaskblog.models import Ciclo
from flaskblog import db

ciclo = Blueprint('ciclo', __name__)

@ciclo.route("/download_cycle_inform/<int:ciclo_id>")
def download_cycle_inform(ciclo_id):
    ciclo = Ciclo.query.get_or_404(ciclo_id)
    return send_file('/home/jorge/autoclave/flaskblog/static/ciclos/C21_07_11_20:50.pdf',attachment_filename='C21_07_11_20:50.pdf')
