from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from flaskblog.models.LineAudit import LineAudit

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    state = db.Column(db.Integer, nullable=False)
    line = db.relationship('LineAudit', backref='audit', lazy=True)


    def __init__(self):

        self.name = "L"+datetime.now().strftime('%y_%m_%d_%H:%M')+".pdf"
        self.state = 0
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

        for lin in self.line:
            textobject.textLine(lin.string.replace("\n","").replace("\r",""))

        ps = ParagraphStyle(textobject, leading=6)
        c.drawText(textobject)
        c.save()


        pass
