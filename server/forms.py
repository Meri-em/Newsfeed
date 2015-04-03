from wtforms.fields import TextAreaField, SubmitField, FileField
from wtforms import Form, validators, TextField, PasswordField

class RegistrationForm(Form):
    username = TextField('Име', [validators.Required('Моля въведете потребителско име')])
    password = PasswordField('Парола', [validators.Required('Моля въведете парола')])
    submit = SubmitField('Създай акаунт')

class LoginForm(Form):
    username = TextField('Име', [validators.Required('Моля въведете потребителско име')])
    password = PasswordField('Парола', [validators.Required('Моля въведете парола')])
    submit = SubmitField('Вход')
