from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from config import UPLOAD_FOLDER

# Cargar variables de entorno desde .env
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)  # Se crea la instancia de Flask
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Se configura la app

    # Configuración usando variables de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    db.init_app(app)
    migrate = Migrate(app, db)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Corregido
    login_manager.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Importar y registrar Blueprints
    from app.routes import routes_bp
    from app.auth import auth_bp
    from app.admin_routes import admin_bp  # Si tienes un Blueprint para admin

    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app