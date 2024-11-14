from flask import request, abort
from flask_restx import Namespace, Resource, fields
from .utils.my_date_format import MyDateFormat
from ..models.cita import Cita
from ..models.paciente import Paciente
from ..models.disponibilidad import Disponibilidad

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
    }
)
cita_input = api.model(
    'CitaField',
    {
        'paciente_id': fields.Integer(required=True, description="ID del paciente"),
        'disponibilidad_id': fields.Integer(required=True, description="ID del disponibilidad"),
        'tipo_cita': fields.String(required=True, description="Tipo de cita"),
        'detalles_adicionales': fields.String(required=True, description="Detalles adicionales de la cita"),
    }
)
@api.route('/agendar')
class AgendarCita(Resource):
    @api.expect(cita_input,validate=True)
    def post(self):
        data = request.get_json()
        paciente_id = int(data['paciente_id'])
        disponibilidad_id = int(data['disponibilidad_id'])
        paciente_asociado = Paciente.find_by_id(paciente_id)
        disponibilidad_asociada = Disponibilidad.find_by_id(disponibilidad_id)

        if not disponibilidad_asociada:
            abort(404, 'No se encontró la disponibilidad')
        elif not paciente_asociado:
            abort(404, 'No se encontro el paciente asociado')

        if disponibilidad_asociada.ocupada == True :
            abort(400, 'La disponibilidad ya está ocupada')

        cita_medica = Cita(
            paciente_id=paciente_id,
            disponibilidad_id=disponibilidad_id,
            tipo_cita=data['tipo_cita'],
            detalles_adicionales=data['detalles_adicionales']
        )
        try:
            cita_medica.save()

            disponibilidad_asociada.ocupada = True
            disponibilidad_asociada.save()

            return {
                'cita_id': cita_medica.id,
                'paciente_id': cita_medica.paciente_id,
                'tipo_cita': cita_medica.tipo_cita,
                'detalles_adicionales': cita_medica.detalles_adicionales,
                'disponibilidad_id': cita_medica.disponibilidad_id
            }, 201
        except Exception as e:
            abort(500, f"Error al agendar la cita: {str(e)}")

@api.route('/delete/<int:cita_id>')
class DeleteCita(Resource):
    def delete(self,cita_id):
        cita=Cita.find_by_id(cita_id)

        if not cita:
            abort(404, f'No existe la cita {cita_id}')
        if cita.estado!="por_confirmar":
            abort(400, 'No se puede eliminar una cita que no est en "por confirmar"')

        try:
            disponibilidad=Disponibilidad.find_by_id(cita.disponibilidad_id)

            if disponibilidad:
                disponibilidad.ocupada=False
                disponibilidad.save()

            cita.delete()
            return '',204

        except Exception as e:
            abort(500, f"Error al eliminar la cita: {str(e)}")
