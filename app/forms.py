from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, URLField, SubmitField
from wtforms.validators import DataRequired, URL
from wtforms.validators import Optional

class NoticiaForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired()])
    descripcion = TextAreaField("Descripción", validators=[DataRequired()])
    poseeImg = BooleanField("¿Tiene Imagen?")
    imagen_url = URLField("URL de la Imagen", validators=[Optional(), URL()])
    poseeVid = BooleanField("¿Tiene Video?")
    video_url = URLField("URL del Video", validators=[Optional(), URL()])
    submit = SubmitField("Publicar Noticia")

from wtforms import PasswordField
from wtforms.validators import Length

class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])  # Asegurar que el nombre coincide con `Usuario.user`
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Iniciar Sesión")