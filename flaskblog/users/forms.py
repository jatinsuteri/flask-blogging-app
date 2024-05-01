from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,FileField
from wtforms.validators import DataRequired,EqualTo,Email,Length,ValidationError
from flaskblog.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')
    

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()   
        if user:
            raise ValidationError('Username Taken, Please choose another username')
        
    def validate_email(self,email):
        email = User.query.filter_by(email = email.data).first()   
        if email:
            raise ValidationError('email Taken, Please choose another email')
        
    
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    password = PasswordField('password', validators=[DataRequired() ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateAccountForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    email = StringField('email', validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpeg','jpg','png'])])
    submit = SubmitField('Update')
    

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()   
            if user:
                raise ValidationError('Username Taken, Please choose another username')
        
    def validate_email(self,email):
        if email.data != current_user.email:
            email = User.query.filter_by(email = email.data).first()   
            if email:
                raise ValidationError('Email Taken, Please choose another email')
   

class RequestResetForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)] )
    submit = SubmitField('Request Password Reset')
    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()   
        if user is None:
            raise ValidationError('There is no account with that username, please create an account')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Request Password Reset')