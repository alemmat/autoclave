from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models.CompanyData import CompanyData
from flaskblog.models.Log import Log
from flaskblog.models.User import User
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm)


users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])

def register():

    companyData = CompanyData.query.first()

    form = RegistrationForm()

    if len( User.query.all() ) < 4:

        if current_user.is_authenticated:
            return redirect(url_for('main.ciclos'))

        if form.validate_on_submit():

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Su cuenta a sido creada. Ahora usted puede loguearse.', 'success')
            return redirect(url_for('users.login'))

    else:
        flash('Ya se han creado todos los usuarios permitidos', 'danger')


    return render_template('register.html', title='Register', form=form, companydata = companyData)


@users.route("/login", methods=['GET', 'POST'])
def login():
    companyData = CompanyData.query.first()
    session.permanent = True
    if current_user.is_authenticated:
        return redirect(url_for('ciclo.show_all_ciclo'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            if user.id != 1:
                log = Log(user_id=user.id)
                db.session.add(log)
                db.session.commit()

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('ciclo.show_all_ciclo'))
        else:
            flash('Clave o usuario incorrecto', 'danger')
    return render_template('login.html', title='Login', form=form, companydata = companyData)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.landing'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    companyData = CompanyData.query.first()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Su cuenta a sido creada', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    return render_template('account.html', title='Account',form=form, companydata = companyData)
