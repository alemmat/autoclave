from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Cycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    state = db.Column(db.Integer, nullable=False)
    line = db.relationship('LineCycle', backref='line', lazy=True)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    state = db.Column(db.Integer, nullable=False)
    line = db.relationship('LineAudit', backref='line', lazy=True)

class LineCycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.String(100), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'), nullable=False)

class LineAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.String(100), nullable=False)
    audit_id = db.Column(db.Integer, db.ForeignKey('audit.id'), nullable=False)

class CompanyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(100), nullable=False)
    devicedesignation = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(100), nullable=False)
