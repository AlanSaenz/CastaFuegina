from app import create_app, db
from app.models import Usuario

app = create_app()
with app.app_context():
    admin = Usuario(user="adminA") 
    admin.set_password("123123")  # Cambia la contraseña por una más segura 
    db.session.add(admin)
    db.session.commit()
    print("Usuario administrador creado")