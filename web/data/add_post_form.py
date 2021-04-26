from flask_wtf import FlaskForm
from wtforms import PasswordField, IntegerField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class AddPostForm(FlaskForm):
    post = StringField('Внеси свою лепту', validators=[DataRequired()])
    submit = SubmitField('Кочерга')
