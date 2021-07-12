from flask import render_template, request, Blueprint
from flaskblog.models import Ciclo
from flaskblog import db

main = Blueprint('main', __name__)


@main.route("/")
def landing():
    page = request.args.get('page', 1, type=int)
    ciclos = Ciclo.query.order_by(Ciclo.date_created.desc()).paginate(page=page, per_page=10)
    return render_template('ciclos.html', ciclos=ciclos)
