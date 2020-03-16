from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ecommerceweb.dbmodel import User


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    contactno = IntegerField('Contact Number')
    addr1 = StringField('Address Line 1', validators=[Length(min=1, max=50)])
    addr2 = StringField('Address Line 2', validators=[Length(max=50)])
    addr3 = StringField('Address Line 3', validators=[Length(max=50)])
    pincode = IntegerField('Pincode')
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    country = StringField('Country', validators=[Length(max=50)])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class ProductForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=100)])
    cost = IntegerField('Cost', validators=[DataRequired()])
    details = StringField('Product Details', validators=[DataRequired(), Length(min=1, max=500)])
    category_id = SelectField('Category', choices=[('1', 'Handicrafts'), ('2', 'Home Decor'), ('3', 'Ayurveda'), ('4', 'Khadi Cloth products'), ('5', 'Spices'), ('6', 'Pickles')])
    image_file1 = FileField('Picture 1', validators=[FileAllowed(['jpg', 'png'])])
    image_file2 = FileField('Picture 2', validators=[FileAllowed(['jpg', 'png'])])
    image_file3 = FileField('Picture 3', validators=[FileAllowed(['jpg', 'png'])])
    image_file4 = FileField('Picture 4', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')