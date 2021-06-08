from flask import render_template, request, Blueprint
from flaskblog.models import Ciclo

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    ciclos = Ciclo.query.order_by(Ciclo.date_created.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', ciclos=ciclos)
