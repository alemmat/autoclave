from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin

from flaskblog.models.LineCycle import LineCycle
from flaskblog.models.TempCycle import TempCycle
from flaskblog.models.PressureCycle import PressureCycle

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

import os

path = '/home/jorge/autoclave/flaskblog/static/ciclos/'

class Cycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    state = db.Column(db.Integer, nullable=False, default = 0)
    lines = db.relationship('LineCycle', backref='cycle', lazy=True)
    temp = db.relationship('TempCycle', backref='cycle', lazy=True)
    pressure = db.relationship('PressureCycle', backref='cycle', lazy=True)

    def __init__(self):

        self.name = "C"+datetime.now().strftime('%y_%m_%d_%H:%M')+".pdf"
        self.state = 0
        db.session.add(self)
        db.session.commit()

    def closeCycle(self):

        self.state = 1
        db.session.commit()


    def insertCycleLine(self, lineString):

        line = LineCycle(string = lineString, cycle_id = self.id)
        db.session.add(line)
        db.session.commit()


    def genaratePdf(self):

        self.closeCycle()

        pdf = canvas.Canvas(path+self.name)
        textobject = pdf.beginText()
        textobject.setTextOrigin(cm, 28.7*cm)

        for line in self.lines:
            textobject.textLine(line.string.replace("\n","").replace("\r",""))

        ps = ParagraphStyle(textobject, leading=6)
        pdf.drawText(textobject)
        pdf.save()

    def delete(self):

        if os.path.isfile(path+self.name):
            os.remove(path+self.name)

        for line in self.lines:
            db.session.delete(line)
            db.session.commit()

        db.session.delete(self)
        db.session.commit()
