from flask import jsonify
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required
from app.models import Usuario
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(user=user).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            return jsonify({'status': 'success', 'message': 'Inicio de sesión exitoso', 'redirect': url_for('admin.gestionar_noticias')})
            # flash("Inicio de sesión exitoso", "success")
            # return redirect(url_for('admin.gestionar_noticias'))
        else:
            return jsonify({'status': 'error', 'message': 'Usuario o contraseña incorrectos'})
            # flash("Usuario o contraseña incorrectos", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión", "info")
    return redirect(url_for('auth.login'))