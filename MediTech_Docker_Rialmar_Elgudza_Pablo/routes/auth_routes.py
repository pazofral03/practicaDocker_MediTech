from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import Usuario
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = Usuario.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Por favor revisa tus credenciales e inténtalo de nuevo.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        flash(f'¡Bienvenido de nuevo, {user.nombre_completo}!', 'success')
        
        # Redirigir a la página siguiente si existe, o al index
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        rol = request.form.get('rol')

        if not all([nombre_completo, email, password, rol]):
            flash('Por favor completa todos los campos obligatorios.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')

        import re
        if re.search(r'@[^@]*\d', email):
            flash('El correo no puede tener números después del arroba.', 'danger')
            return render_template('register.html')

        # Validar si existe
        if Usuario.query.filter_by(email=email).first():
            flash('Error: El email ya está registrado.', 'danger')
            return render_template('register.html')

        from werkzeug.security import generate_password_hash
        
        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            email=email,
            password=generate_password_hash(password),
            rol=rol
        )

        # Campos específicos
        if rol == 'medico':
            nuevo_usuario.num_colegiado = request.form.get('num_colegiado')
            nuevo_usuario.especialidad = request.form.get('especialidad')
            nuevo_usuario.disponibilidad = request.form.get('disponibilidad')
        elif rol == 'paciente':
            nuevo_usuario.nss = request.form.get('nss')
            nuevo_usuario.telefono = request.form.get('telefono')
            
            if nuevo_usuario.telefono and not nuevo_usuario.telefono.isdigit():
                 flash('El teléfono solo debe contener números.', 'danger')
                 return render_template('register.html')

            nuevo_usuario.direccion = request.form.get('direccion')

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Login automático
            login_user(nuevo_usuario)
            flash(f'¡Bienvenido, {nuevo_usuario.nombre_completo}! Registro exitoso.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar usuario: {str(e)}', 'danger')

    return render_template('register.html')
