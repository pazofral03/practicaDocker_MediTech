from werkzeug.security import generate_password_hash
from datetime import datetime
from database import db  # Importamos la conexión que acabamos de crear

def reiniciar_base_ de_datos():
    users_collection = db['usuarios']
    
    # 1. Borramos todo
    users_collection.drop()
    print("--- Colección de usuarios borrada ---")

    # 2. Definimos los datos (UML)
    usuarios_semilla = [
        # --- ADMIN ---
        {
            "email": "admin@meditech.com",
            "password": generate_password_hash("admin123"),
            "nombre_completo": "Super Administrador",
            "rol": "admin",
            "fecha_registro": datetime.now()
        },
        # --- MÉDICOS ---
        {
            "email": "house@meditech.com",
            "password": generate_password_hash("medico123"),
            "nombre_completo": "Dr. Gregory House",
            "rol": "medico",
            "num_colegiado": "MED-001",
            "especialidad": "Diagnóstico",
            "disponibilidad": ["Lunes", "Viernes"],
            "fecha_registro": datetime.now()
        },
        {
            "email": "strange@meditech.com",
            "password": generate_password_hash("medico123"),
            "nombre_completo": "Dr. Stephen Strange",
            "rol": "medico",
            "num_colegiado": "MED-999",
            "especialidad": "Cirugía",
            "disponibilidad": ["Martes"],
            "fecha_registro": datetime.now()
        },
        # --- PACIENTES ---
        {
            "email": "pepe@gmail.com",
            "password": generate_password_hash("paciente123"),
            "nombre_completo": "Pepe Pérez",
            "rol": "paciente",
            "nss": "1234567890",
            "telefono": "600111222",
            "direccion": "Calle Falsa 123",
            "fecha_registro": datetime.now()
        }
    ]

    # 3. Insertamos
    users_collection.insert_many(usuarios_semilla)
    print(f"--- {len(usuarios_semilla)} usuarios insertados ---")