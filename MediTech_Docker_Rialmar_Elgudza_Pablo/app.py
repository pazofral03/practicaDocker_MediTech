import os
from flask import Flask, render_template
from extensions import db, login_manager
from models import Usuario

# Import Routes
from routes.usuarios_routes import usuarios_bp
from routes.auth_routes import auth_bp
from routes.citas_routes import citas_bp

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'clave_dev')

# Configuración de SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'meditech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar
db.init_app(app)
login_manager.init_app(app)

# Loader de usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- REGISTRO DE BLUEPRINTS ---
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(citas_bp)

# --- RUTA PRINCIPAL ---
@app.route('/')
def index():
    from flask_login import current_user
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.context_processor
def inject_now():
    from datetime import date
    return {'get_today_date': date.today().isoformat()}