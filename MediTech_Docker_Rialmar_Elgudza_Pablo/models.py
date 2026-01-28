from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin, medico, paciente
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Datos para médico
    especialidad = db.Column(db.String(100), nullable=True)
    num_colegiado = db.Column(db.String(50), nullable=True)
    disponibilidad = db.Column(db.String(200), nullable=True)
    
    # Datos para paciente
    nss = db.Column(db.String(50), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)

    # Relaciones para facilitar consultas de citas
    citas_como_medico = db.relationship('Cita', foreign_keys='Cita.medico_id', backref='medico', lazy=True)
    citas_como_paciente = db.relationship('Cita', foreign_keys='Cita.paciente_id', backref='paciente', lazy=True)
    
    # Relacion de ausencias (médico)
    ausencias = db.relationship('Ausencia', backref='medico', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre_completo}>'

class Cita(db.Model):
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    motivo_consulta = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(50), default='Pendiente') # Pendiente, Confirmada, Completada, Cancelada
    
    # Diagnóstico y Tratamiento (rellenados por médico)
    diagnostico = db.Column(db.Text, nullable=True)
    tratamiento = db.Column(db.Text, nullable=True)

    # Relaciones
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return f'<Cita {self.id} - {self.fecha_hora}>'

class Ausencia(db.Model):
    __tablename__ = 'ausencias'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Ausencia {self.medico_id}: {self.fecha_inicio} - {self.fecha_fin}>'
