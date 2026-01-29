from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from datetime import datetime
from extensions import db
from models import Usuario
import re

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios')
def index():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/crear', methods=['GET', 'POST'])
def crear():
    # Objeto para preservar datos en caso de error
    datos_formulario = None
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')
        
        # Recopilar datos para repoblar formulario
        datos_formulario = {
            'nombre_completo': nombre_completo,
            'email': email,
            'rol': rol,
            'num_colegiado': request.form.get('num_colegiado') or '',
            'especialidad': request.form.get('especialidad') or '',
            'disponibilidad': request.form.get('disponibilidad') or '',
            'nss': request.form.get('nss') or '',
            'telefono': request.form.get('telefono') or '',
            'direccion': request.form.get('direccion') or ''
        }

        # Validación básica
        if not all([nombre_completo, email, password, rol]):
            flash('Por favor completa todos los campos obligatorios.', 'danger')
            return render_template('usuario_form.html', usuario=datos_formulario)

        if re.search(r'@[^@]*\d', email):
            flash('El correo no puede tener números después del arroba.', 'danger')
            return render_template('usuario_form.html', usuario=datos_formulario)

        # Validar email único
        if Usuario.query.filter_by(email=email).first():
            flash('Error: El email ya está registrado.', 'danger')
            return render_template('usuario_form.html', usuario=datos_formulario)

        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            email=email,
            password=generate_password_hash(password),
            rol=rol,
            fecha_registro=datetime.now()
        )

        # Campos específicos
        if rol == 'medico':
            nuevo_usuario.num_colegiado = datos_formulario['num_colegiado']
            nuevo_usuario.especialidad = datos_formulario['especialidad']
            nuevo_usuario.disponibilidad = datos_formulario['disponibilidad']
        elif rol == 'paciente':
            nuevo_usuario.nss = datos_formulario['nss']
            nuevo_usuario.telefono = datos_formulario['telefono']
            
            if nuevo_usuario.telefono and not nuevo_usuario.telefono.isdigit():
                 flash('El teléfono solo debe contener números.', 'danger')
                 return render_template('usuario_form.html', usuario=datos_formulario)

            nuevo_usuario.direccion = datos_formulario['direccion']

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
            return render_template('usuario_form.html', usuario=datos_formulario)

    return render_template('usuario_form.html', usuario=None)

@usuarios_bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        # Verificar duplicidad de email (excluyendo el propio usuario)
        nuevo_email = request.form.get('email')
        
        if re.search(r'@[^@]*\d', nuevo_email):
            flash('El correo no puede tener números después del arroba.', 'danger')
            return render_template('usuario_form.html', usuario=usuario)

        usuario_existente = Usuario.query.filter_by(email=nuevo_email).first()
        
        if usuario_existente and usuario_existente.id != id:
            flash('Error: El email ya está en uso por otro usuario.', 'danger')
            # No actualizamos nada y volvemos a mostrar la página
            return render_template('usuario_form.html', usuario=usuario)

        usuario.nombre_completo = request.form.get('nombre_completo')
        usuario.email = nuevo_email
        usuario.rol = request.form.get('rol')
        
        # Actualizar password solo si se escribe una nueva
        password_nueva = request.form.get('password')
        if password_nueva:
            usuario.password = generate_password_hash(password_nueva)

        # Campos específicos (limpiamos los otros por si cambió de rol)
        if usuario.rol == 'medico':
            usuario.num_colegiado = request.form.get('num_colegiado')
            usuario.especialidad = request.form.get('especialidad')
            usuario.disponibilidad = request.form.get('disponibilidad')
            # Limpiar datos paciente
            usuario.nss = None; usuario.telefono = None; usuario.direccion = None;
        elif usuario.rol == 'paciente':
            usuario.nss = request.form.get('nss')
            usuario.telefono = request.form.get('telefono')
            
            if usuario.telefono and not usuario.telefono.isdigit():
                 flash('El teléfono solo debe contener números.', 'danger')
                 return render_template('usuario_form.html', usuario=usuario)

            usuario.direccion = request.form.get('direccion')
            # Limpiar datos medico
            usuario.num_colegiado = None; usuario.especialidad = None; usuario.disponibilidad = None;
        else:
            # Si es admin, limpiar todo
            usuario.num_colegiado = None; usuario.especialidad = None; usuario.disponibilidad = None;
            usuario.nss = None; usuario.telefono = None; usuario.direccion = None;

        try:
            db.session.commit()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
            # En caso de error, usuario (objeto de sesión) puede tener datos sucios, 
            # pero el rollback debería haberlos limpiado.
            return render_template('usuario_form.html', usuario=usuario)

    return render_template('usuario_form.html', usuario=usuario)

@usuarios_bp.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
        
    return redirect(url_for('usuarios.index'))


