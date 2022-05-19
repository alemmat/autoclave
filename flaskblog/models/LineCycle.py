from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin

class LineCycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string = db.Column(db.String(100), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'), nullable=False)
