from flask_restx import Namespace, fields
from .utils.my_date_format import MyDateFormat

api = Namespace('cita', description='endpoints para visualizar cita médica')

especialista_input = api.model(
    'EspecialistaRegisterFields',
    {
        'especialidad': fields.String(required=True),
        'primer_nombre': fields.String(required=True),
        'primer_apellido': fields.String(required=True),
    }
)

bloque_input = api.model(
    'BloqueDeDisponibilidad',
    {
        'fecha': MyDateFormat(required=True, description='Fecha en formato YYYY-MM-DD'),
        'hora_inicio': fields.String(required=True, description="Hora de inicio en formato HH:MM"),
        'hora_fin': fields.String(required=True, description="Hora de fin en formato HH:MM")
    }
)

disponibilidad_input = api.model(
    'Disponibilidad',
    {
        'especialista_id': fields.Integer(required=True, description="ID del especialista"),
        'bloque': fields.Nested(bloque_input, required=True, description="Datos del bloque de disponibilidad")
    }
)
