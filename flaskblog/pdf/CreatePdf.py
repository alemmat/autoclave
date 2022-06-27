from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle


class CreatePdf():

    def __init__(self, name, lines):

        pdf = canvas.Canvas(name)
        textobject = pdf.beginText()
        textobject.setTextOrigin(0.1*cm, 28.7*cm)

        for line in lines:
            textobject.textLine(line.replace("\n","").replace("\r",""))

        ps = ParagraphStyle(textobject, leading=6)
        pdf.drawText(textobject)
        pdf.save()
