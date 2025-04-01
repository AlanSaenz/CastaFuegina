from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    noticia_id = db.Column(db.Integer, db.ForeignKey('noticia.id'), nullable=False)
    archivo = db.Column(db.String(300), nullable=False)

    noticia = db.relationship('Noticia', back_populates='imagenes')

class Comentario_Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    noticia_id = db.Column(db.Integer, db.ForeignKey('noticia.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

    noticia = db.relationship('Noticia', back_populates='comentarios')

class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    subtitulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    poseeImg = db.Column(db.Boolean, default=False)
    poseeVid = db.Column(db.Boolean, default=False)
    video = db.Column(db.String(300))
    fecha_publicacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    imagenes = db.relationship('Imagen', back_populates='noticia', cascade="all, delete-orphan")
    comentarios = db.relationship('Comentario_Noticia', back_populates='noticia', cascade="all, delete-orphan")


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())