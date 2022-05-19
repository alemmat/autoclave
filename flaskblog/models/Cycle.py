from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog.models.LineCycle import LineCycle
from flaskblog.models.TempCycle import TempCycle
from flaskblog.models.PressureCycle import PressureCycle

class Cycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    state = db.Column(db.Integer, nullable=False)
    line = db.relationship('LineCycle', backref='cycle', lazy=True)
    temp = db.relationship('TempCycle', backref='cycle', lazy=True)
    pressure = db.relationship('PressureCycle', backref='cycle', lazy=True)
