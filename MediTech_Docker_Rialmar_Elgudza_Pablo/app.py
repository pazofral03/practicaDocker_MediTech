import os
from flask import Flask, render_template
from routes.usuarios_routes import usuarios_bp # Importamos las rutas

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'clave_dev')

# --- REGISTRO DE BLUEPRINTS ---
# Aquí decimos: "Todo lo que esté en usuarios_bp, añádelo a mi app"
app.register_blueprint(usuarios_bp)

# --- RUTA PRINCIPAL ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)