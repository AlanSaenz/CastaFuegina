import uuid
from flask import Flask, jsonify, render_template, Blueprint, request, redirect, url_for, flash
import os
from flask import current_app
from app.models import db, Noticia, Imagen, Comentario, Comentario_Noticia
from werkzeug.utils import secure_filename
import requests
# from config import UPLOAD_FOLDER

routes_bp = Blueprint('routes', __name__)

# Extensiones permitidas para imágenes y videos
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Ruta para verificar si es un archivo valido
def allowed_file(filename, file_types):
    """Verifica si la extensión del archivo es válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in file_types

@routes_bp.route("/")
def index():
    noticias = Noticia.query.order_by(Noticia.fecha_publicacion.desc()).all()
    comentarios = Comentario.query.order_by(Comentario.fecha.desc()).limit(10).all()
    return render_template("index.html", noticias=noticias, comentarios=comentarios)

@routes_bp.route('/agregar_comentario', methods=['POST'])
def agregar_comentario():
    nombre = request.form.get('nombre')
    texto = request.form.get('texto')
    if nombre and texto:
        nuevo_comentario = Comentario(nombre=nombre, texto=texto)
        db.session.add(nuevo_comentario)
        db.session.commit()
        return jsonify({'success': True, 'nombre': nombre, 'texto': texto})
    return jsonify({'success': False})

@routes_bp.route('/clima')
def obtener_clima():
    api_key = 'xs4dgdzi2in88wt82csoxgb2yf9m18mquyj7zpws'
    lugarID = 'postal-ar-9420'
    url = f'https://www.meteosource.com/api/v1/free/point?place_id={lugarID}&sections=current%2Chourly&timezone=auto&language=en&units=auto&key={api_key}'
    respuesta = requests.get(url)
    datos_clima = respuesta.json()

    # Diccionario de traducciones de términos climáticos comunes
    traducciones = {
        "Clear": "Despejado",
        "Partly cloudy": "Parcialmente nublado",
        "Cloudy": "Nublado",
        "Overcast": "Cubierto",
        "Rain": "Lluvia",
        "Light rain": "Lluvia ligera",
        "Heavy rain": "Lluvia intensa",
        "Snow": "Nieve",
        "Fog": "Niebla",
        "Thunderstorm": "Tormenta eléctrica",
        "Drizzle": "Llovizna",
        "Sunny": "Soleado",
        "Showers": "Chaparrones"
    }

    # Traducir la descripción del clima
    clima_actual = datos_clima.get("current", {})
    descripcion_en = clima_actual.get("summary", "No disponible")
    temperatura = clima_actual.get("temperature", "No disponible")
    
    descripcion_es = traducciones.get(descripcion_en, descripcion_en)  # Si no encuentra, deja la original

    return jsonify({"descripcion": descripcion_es, "temperatura": temperatura})

@routes_bp.route('/noticia/<int:noticia_id>')
def noticia_detalle(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    return render_template('noticia_detalle.html', noticia=noticia)

@routes_bp.route("/eliminar_comentario/<int:id>", methods=["POST"])
def eliminar_comentario(id):
    comentario = Comentario.query.get(id)
    if comentario:
        db.session.delete(comentario)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Comentario no encontrado"})

@routes_bp.route('/noticia/agregar', methods=['GET', 'POST'])
def agregar_noticia():
    if request.method == 'POST':
        titulo = request.form['titulo']
        subtitulo = request.form['subtitulo']
        descripcion = request.form['descripcion']
        poseeImg = 'poseeImg' in request.form
        poseeVid = 'poseeVid' in request.form

        # Crear noticia en la BD
        nueva_noticia = Noticia(
            titulo=titulo,
            subtitulo=subtitulo,
            descripcion=descripcion,
            poseeImg=False,  # Se actualizará más tarde si se sube imagen
            poseeVid=poseeVid,  # Se actualizará si se sube video
            video=None
        )
        db.session.add(nueva_noticia)
        db.session.commit()  # Ahora tiene un ID asignado

        noticia_id = nueva_noticia.id  # Obtener el ID de la noticia
        upload_folder = os.path.join(os.path.dirname(__file__), 'static/uploads')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        imagen_filenames = []  # Para almacenar los nombres de archivo de las imágenes

        # Procesar imágenes
        if poseeImg and 'imagenes' in request.files:
            imagenes = request.files.getlist('imagenes')  # Obtener todas las imágenes
            for i, imagen in enumerate(imagenes):
                if imagen and allowed_file(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                    ext = imagen.filename.rsplit('.', 1)[1].lower()
                    imagen_filename = f"noticia_{noticia_id}_img_{i + 1}.{ext}"
                    imagen_path = os.path.join(upload_folder, imagen_filename)
                    imagen.save(imagen_path)

                    # Guardar imagen en la base de datos
                    nueva_imagen = Imagen(archivo=imagen_filename, noticia_id=noticia_id)
                    db.session.add(nueva_imagen)
                    imagen_filenames.append(imagen_filename)
                else:
                    flash(f"Formato de imagen {i+1} no válido.", 'danger')
                    return redirect(request.url)

            nueva_noticia.poseeImg = True

        # Procesar video (si se sube)
        if poseeVid and 'video' in request.files:
            video = request.files['video']
            if video and allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
                ext = video.filename.rsplit('.', 1)[1].lower()
                video_filename = f"noticia_{noticia_id}_vid_1.{ext}"
                video_path = os.path.join(upload_folder, video_filename)
                video.save(video_path)
                nueva_noticia.video = video_filename
            else:
                flash('Formato de video no válido.', 'danger')
                return redirect(request.url)

        db.session.commit()
        flash('Noticia agregada con éxito', 'success')
        return redirect(url_for('admin.gestionar_noticias'))

    return render_template('agregar_noticia.html')

# Ruta para editar una noticia
@routes_bp.route('/noticia/editar/<int:noticia_id>', methods=['GET', 'POST'])
def editar_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)

    if request.method == 'POST':
        noticia.titulo = request.form['titulo']
        noticia.subtitulo = request.form['subtitulo']
        noticia.descripcion = request.form['descripcion']

        upload_folder = os.path.join(os.path.dirname(__file__), 'static/uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # ✅ Eliminar imágenes si el checkbox está marcado
        if 'eliminar_imagenes' in request.form:
            for imagen in noticia.imagenes:
                image_path = os.path.join(upload_folder, imagen.archivo)
                if os.path.exists(image_path):
                    os.remove(image_path)
                db.session.delete(imagen)
            noticia.imagenes.clear()  # Eliminar referencias
            noticia.poseeImg = False

        # ✅ Manejo de nuevas imágenes
        if 'imagenes' in request.files:
            imagenes = request.files.getlist('imagenes')
            for i, imagen in enumerate(imagenes):
                if imagen and allowed_file(imagen.filename, ALLOWED_IMAGE_EXTENSIONS):
                    ext = imagen.filename.rsplit('.', 1)[1].lower()
                    imagen_filename = f"noticia_{noticia.id}_img_{i}.{ext}"
                    imagen.save(os.path.join(upload_folder, imagen_filename))
                    
                    nueva_imagen = Imagen(noticia_id=noticia.id, archivo=imagen_filename)
                    db.session.add(nueva_imagen)

            if imagenes:
                noticia.poseeImg = True

        # ✅ Eliminar video si el checkbox está marcado
        if 'eliminar_video' in request.form and noticia.video:
            video_path = os.path.join(upload_folder, noticia.video)
            if os.path.exists(video_path):
                os.remove(video_path)
            noticia.video = None
            noticia.poseeVid = False

        # ✅ Manejo de nuevo video
        if 'video' in request.files and request.files['video'].filename:
            video = request.files['video']
            if video and allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
                ext = video.filename.rsplit('.', 1)[1].lower()
                video_filename = f"noticia_{noticia.id}_vid_1.{ext}"
                
                # Eliminar video anterior si existe
                if noticia.video:
                    old_video_path = os.path.join(upload_folder, noticia.video)
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)

                video.save(os.path.join(upload_folder, video_filename))
                noticia.video = video_filename
                noticia.poseeVid = True

        db.session.commit()
        flash("Noticia actualizada con éxito", "success")
        return redirect(url_for('admin.gestionar_noticias'))

    return render_template('editar_noticia.html', noticia=noticia)

# Ruta para eliminar un comentario de la noticia.
@routes_bp.route('/comentario/eliminar/<int:comentario_id>', methods=['POST'])
def eliminar_comentario_noticia(comentario_id):
    comentario = Comentario_Noticia.query.get(comentario_id)

    if not comentario:
        return jsonify({"success": False, "error": "Comentario no encontrado"}), 404

    db.session.delete(comentario)
    db.session.commit()

    return jsonify({"success": True})


# Ruta para eliminar una noticia
@routes_bp.route('/noticia/eliminar/<int:noticia_id>', methods=['POST'])
def eliminar_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    db.session.delete(noticia)
    db.session.commit()
    flash('Noticia eliminada correctamente', 'danger')
    return redirect(url_for('admin.gestionar_noticias'))

# 
@routes_bp.route('/noticia/<int:noticia_id>/comentar', methods=['POST'])
def agregar_comentario_noticia(noticia_id):
    nombre = request.form.get('nombre')
    comentario_texto = request.form.get('comentario')

    if not nombre or not comentario_texto:
        return jsonify({"success": False, "message": "Por favor, completa todos los campos."})

    nuevo_comentario = Comentario_Noticia(noticia_id=noticia_id, nombre=nombre, texto=comentario_texto)

    db.session.add(nuevo_comentario)
    db.session.commit()

    return jsonify({"success": True})

# 
@routes_bp.route('/noticia/<int:noticia_id>/comentarios')
def obtener_comentarios(noticia_id):
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    paginacion = Comentario_Noticia.query.filter_by(noticia_id=noticia_id) \
                .order_by(Comentario_Noticia.fecha.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)

    comentarios = [
        {"nombre": c.nombre, "texto": c.texto, "fecha": c.fecha.strftime('%d/%m/%Y')}
        for c in paginacion.items
    ]

    return jsonify({
        "comentarios": comentarios,
        "pagina": page,
        "total_paginas": paginacion.pages,
        "has_more": paginacion.has_next
    })