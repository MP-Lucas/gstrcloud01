from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, IPAddress, Length
from .models import User

# Formulário de login do usuário
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8, max=32)])
    remember = BooleanField('Manter-se conectado')
    submit = SubmitField('Entrar')

# Formulário de registro de usuário
class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8, max=32)])
    password2 = PasswordField(
        'Repita a senha', validators=[DataRequired(), Length(min=8, max=32), EqualTo('password')])
    submit = SubmitField('Registrar-se')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Use um nome de usuário diferente')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Use um endereo de e-mail diferente')


# Formulário de cadastro de robôs
class RobotForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    ip_address = StringField('Endereço IP', validators=[DataRequired(), IPAddress()])
    port = IntegerField('Porta', validators=[DataRequired()])
    robot_id = StringField('ID do Robô', validators=[DataRequired()])
    robot_password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Registrar Robô')
