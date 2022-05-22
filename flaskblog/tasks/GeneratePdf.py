from flaskblog import celery
from datetime import datetime, date, time, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

@celery.task
def closeOldAudits():
    print("hola")
