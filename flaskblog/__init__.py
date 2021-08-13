from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

from datetime import timedelta


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{username}:{password}@{server}:3306/db_autoclave".format(username = "user", password = "123", server = "127.0.0.1")


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.main.routes import main
    from flaskblog.ciclo.routes import ciclo
    from flaskblog.audit.routes import audit
    from flaskblog.companydata.routes import companydata
    from flaskblog.log.routes import log

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(ciclo)
    app.register_blueprint(audit)
    app.register_blueprint(companydata)
    app.register_blueprint(log)

    return app
