from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import Cita, Usuario, Ausencia
from extensions import db

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/citas')
@login_required
def index():
    if current_user.rol == 'admin':
        citas = Cita.query.order_by(Cita.fecha_hora.desc()).all()
    elif current_user.rol == 'medico':
        citas = Cita.query.filter_by(medico_id=current_user.id).order_by(Cita.fecha_hora.asc()).all()
    else: # Paciente
        citas = Cita.query.filter_by(paciente_id=current_user.id).order_by(Cita.fecha_hora.desc()).all()
    
    return render_template('citas_lista.html', citas=citas)

# --- RUTAS MÉDICO ---

@citas_bp.route('/medico/agenda')
@login_required
def medico_agenda():
    if current_user.rol != 'medico':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('citas.index'))
    return render_template('medico_agenda.html')

@citas_bp.route('/api/citas/medico')
@login_required
def api_citas_medico():
    if current_user.rol != 'medico':
        return jsonify([])
    
    citas = Cita.query.filter_by(medico_id=current_user.id).all()
    eventos = []
    for cita in citas:
        color = '#3788d8' # Default blue
        if cita.estado == 'Confirmada': color = '#17a2b8'
        elif cita.estado == 'Completada': color = '#28a745'
        elif cita.estado == 'Cancelada': color = '#dc3545'
        
        eventos.append({
            'title': f"{cita.paciente.nombre_completo}",
            'start': cita.fecha_hora.isoformat(),
            'url': url_for('citas.gestionar', id=cita.id),
            'color': color,
            'extendedProps': {
                'motivo': cita.motivo_consulta,
                'estado': cita.estado
            }
        })
    return jsonify(eventos)

@citas_bp.route('/medico/ausencias', methods=['GET', 'POST'])
@login_required
def medico_ausencias():
    if current_user.rol != 'medico':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('citas.index'))

    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        motivo = request.form.get('motivo')
        
        try:
            inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            if inicio_dt > fin_dt:
                flash('La fecha de inicio no puede ser posterior a la fecha de fin.', 'warning')
            else:
                nueva_ausencia = Ausencia(
                    medico_id=current_user.id,
                    fecha_inicio=inicio_dt,
                    fecha_fin=fin_dt,
                    motivo=motivo
                )
                db.session.add(nueva_ausencia)
                db.session.commit()
                flash('Ausencia registrada correctamente.', 'success')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
        except Exception as e:
            flash(f'Error al registrar ausencia: {str(e)}', 'danger')

    ausencias = Ausencia.query.filter_by(medico_id=current_user.id).order_by(Ausencia.fecha_inicio.asc()).all()
    return render_template('medico_ausencias.html', ausencias=ausencias)

@citas_bp.route('/medico/ausencias/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_ausencia(id):
    ausencia = Ausencia.query.get_or_404(id)
    if ausencia.medico_id != current_user.id:
        flash('No tienes permiso para eliminar esta ausencia.', 'danger')
        return redirect(url_for('citas.medico_ausencias'))
        
    db.session.delete(ausencia)
    db.session.commit()
    flash('Ausencia eliminada.', 'success')
    return redirect(url_for('citas.medico_ausencias'))

@citas_bp.route('/citas/solicitar', methods=['GET', 'POST'])
@login_required
def solicitar():
    # Solo pacientes o admin pueden solicitar citas nuevas
    if current_user.rol == 'medico':
        flash('Los médicos no pueden solicitar citas para sí mismos.', 'warning')
        return redirect(url_for('citas.index'))

    if request.method == 'POST':
        medico_id = request.form.get('medico_id')
        fecha_str = request.form.get('fecha')
        hora_str = request.form.get('hora')
        motivo = request.form.get('motivo_consulta')
        
        # Combinar fecha y hora
        try:
            fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Formato de fecha u hora inválido.', 'danger')
            return redirect(url_for('citas.solicitar'))

        # Si es admin, puede elegir el paciente
        paciente_id = current_user.id
        if current_user.rol == 'admin' and request.form.get('paciente_id'):
            paciente_id = request.form.get('paciente_id')

        nueva_cita = Cita(
            medico_id=medico_id,
            paciente_id=paciente_id,
            fecha_hora=fecha_hora,
            motivo_consulta=motivo,
            estado='Pendiente'
        )

        try:
            db.session.add(nueva_cita)
            db.session.commit()
            flash('Cita solicitada correctamente.', 'success')
            return redirect(url_for('citas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al solicitar cita: {str(e)}', 'danger')

    # Obtener médicos para el select
    medicos = Usuario.query.filter_by(rol='medico').all()
    # Obtener pacientes si es admin
    pacientes = Usuario.query.filter_by(rol='paciente').all() if current_user.rol == 'admin' else []
    
    return render_template('cita_form.html', medicos=medicos, pacientes=pacientes)

@citas_bp.route('/citas/<int:id>/gestionar', methods=['GET', 'POST'])
@login_required
def gestionar(id):
    cita = Cita.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.rol == 'paciente' and cita.paciente_id != current_user.id:
        flash('No tienes permiso para ver esta cita.', 'danger')
        return redirect(url_for('citas.index'))
    if current_user.rol == 'medico' and cita.medico_id != current_user.id:
        flash('No tienes permiso para gestionar esta cita.', 'danger')
        return redirect(url_for('citas.index'))

    if request.method == 'POST':
        # Médicos pueden actualizar estado, diagnóstico y tratamiento
        if current_user.rol in ['medico', 'admin']:
            cita.diagnostico = request.form.get('diagnostico')
            cita.tratamiento = request.form.get('tratamiento')
            cita.estado = request.form.get('estado')
        
        # Pacientes solo pueden cancelar (o cambiar nota si se quisiera)
        if current_user.rol == 'paciente':
             # Podríamos permitir cancelar si no ha pasado la fecha
             if request.form.get('accion') == 'cancelar':
                 cita.estado = 'Cancelada'

        try:
            db.session.commit()
            flash('Cita actualizada correctamente.', 'success')
            return redirect(url_for('citas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cita: {str(e)}', 'danger')

    return render_template('cita_gestion.html', cita=cita)

@citas_bp.route('/citas/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.rol != 'admin':
        flash('Solo los administradores pueden eliminar citas del registro.', 'danger')
        return redirect(url_for('citas.index'))
        
    cita = Cita.query.get_or_404(id)
    try:
        db.session.delete(cita)
        db.session.commit()
        flash('Cita eliminada permanentemente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
        
    return redirect(url_for('citas.index'))
