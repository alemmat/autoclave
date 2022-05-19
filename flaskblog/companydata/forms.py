from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp

from flaskblog.models.CompanyData import CompanyData

class UpdateCompanyDataForm(FlaskForm):
    companyname = StringField('Nombre de la empresa', validators=[DataRequired()])
    devicedesignation = StringField('Designacion del dispositivo')
    ip = StringField('Dirección ip', validators=[DataRequired(), Length(max=15)])
    submit = SubmitField('Update')
