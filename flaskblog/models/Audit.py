from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog.models.LineAudit import LineAudit

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

import os

path = '/home/jorge/autoclave/flaskblog/static/audits/'

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.now)
    state = db.Column(db.Integer, nullable = False, default = 0)
    lines = db.relationship('LineAudit', backref='audit', lazy = True)


    def __init__(self):

        self.name = "L"+datetime.now().strftime('%y_%m_%d_%H:%M')+".pdf"
        db.session.add(self)
        db.session.commit()


    def closeAudit(self):

        self.state = 1
        db.session.commit()


    def insertAuditLine(self, lineString):

        line = LineAudit(string = lineString, audit_id = self.id)
        db.session.add(line)
        db.session.commit()


    def genaratePdf(self):

        self.closeAudit()

        c = canvas.Canvas(path+audit.name)
        textobject = c.beginText()
        textobject.setTextOrigin(cm, 28.7*cm)

        for line in self.lines:
            textobject.textLine(lin.string.replace("\n","").replace("\r",""))

        ps = ParagraphStyle(textobject, leading=6)
        c.drawText(textobject)
        c.save()


    def delete(self):

        if os.path.isfile(path+self.name):
            os.remove(path+self.name)

        for line in self.lines:
            db.session.delete(line)
            db.session.commit()

        db.session.delete(self)
        db.session.commit()
