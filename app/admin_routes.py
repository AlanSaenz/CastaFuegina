from flask import jsonify, render_template, request, redirect, url_for, flash, Blueprint
from app import db
from app.models import Noticia, Comentario
from flask_login import login_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/noticias', methods=['GET', 'POST'])
@login_required
def gestionar_noticias():
    noticias = Noticia.query.order_by(Noticia.fecha_publicacion.desc()).all()
    comentarios = Comentario.query.order_by(Comentario.fecha.desc()).all()
    return render_template('admin/noticias.html', noticias=noticias, comentarios=comentarios)

@admin_bp.route("/eliminar_comentario/<int:id>", methods=["POST"])
def eliminar_comentario(id):
    comentario = Comentario.query.get(id)
    if comentario:
        db.session.delete(comentario)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})