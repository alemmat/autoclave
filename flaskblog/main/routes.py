from flask import render_template, request, Blueprint
from flaskblog.models import Ciclo
from flaskblog import db

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/ciclos/")
def ciclos():
    page = request.args.get('page', 1, type=int)
    ciclos = Ciclo.query.order_by(Ciclo.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('ciclos.html', ciclos=ciclos)

@main.route("/auditorias")
def auditorias():
    page = request.args.get('page', 1, type=int)
    ciclos = Ciclo.query.order_by(Ciclo.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('ciclos.html', ciclos=ciclos)

@main.route("/ciclo/<int:ciclo_id>")
def downliad_cycle_inform(ciclo_id):
    return render_template('prueba.html')
