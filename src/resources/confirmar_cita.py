from flask import abort, jsonify
from flask_restx import Namespace
from resources.utils.emails_utils import send_email_confirmation
from src.models.paciente import Paciente
from src.models.cita import Cita


api = Namespace('confimar_cita', description='Endpoint para confirmar la cita médica')

@api.route('/confirmar_cita/<int:cita_id>', methods=['POST'])
def confirmar_cita(cita_id):

    # Buscar cita en base de datos
    cita = Cita.query.get(cita_id)
    if not cita:
        abort(404, 'No se encontró la cita')

    # Obtener información del paciente
    paciente = Paciente.query.get(cita.paciente_id)

    # Actualizar estado de la cita
    cita.estado = "cita confirmada"

    send_email_confirmation(paciente.correo, paciente.primer_nombre, cita.id)

    return jsonify({'message': 'Cita confirmada y correo enviado'}), 200