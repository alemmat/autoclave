from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin

class CompanyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(100), nullable=False)
    devicedesignation = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(100), nullable=False)
