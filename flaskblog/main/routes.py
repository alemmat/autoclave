from flask import render_template, request, Blueprint, redirect, url_for

main = Blueprint('main', __name__)

@main.route("/")
def landing():
    return redirect(url_for('ciclo.show_all_ciclo'))
