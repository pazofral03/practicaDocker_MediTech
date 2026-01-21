from flask import Blueprint, render_template, redirect, url_for, flash
from database import db
from seed import reiniciar_base_de_datos

# Creamos el Blueprint (es como una mini-aplicación)
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios')
def ver_usuarios():
    # Usamos la conexión importada de database.py
    usuarios = list(db['usuarios'].find())
    return render_template('usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/init-db')
def seed_db():
    # Llamamos a la función que está en el otro archivo
    try:
        reiniciar_base_de_datos()
        flash("✅ Base de datos reiniciada correctamente.", "success")
    except Exception as e:
        flash(f"❌ Error al reiniciar: {e}", "danger")
        
    return redirect(url_for('usuarios.ver_usuarios')) # Nota: 'usuarios.' es el nombre del blueprint