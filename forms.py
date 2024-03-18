from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired, email, Length,EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    email = StringField('email', validators=[DataRequired(), email()])
    password = PasswordField('password', validators=[DataRequired() ])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(),EqualTo('passowrd')])
    sumbit = SubmitField('Sign Up')
    
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    password = PasswordField('password', validators=[DataRequired() ])
    submit = SubmitField('Login')
    remember = BooleanField('Remember Me')
    