from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo

from .models.auth import User


class SignupForm(FlaskForm):
    name = StringField('fullname', validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField('login', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('load avatar', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Sign up')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('That login is already used, you will have to select another.')
        
class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('remember me')
    submit = SubmitField('Submit')