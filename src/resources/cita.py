from flask import request, abort
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import SQLAlchemyError
from .utils.my_date_format import MyDateFormat
from ..models.bloque_de_disponibilidad import BloqueDeDisponibilidad
from ..models.cita import Cita
from ..models.especialidad import Especialidad
from ..models.paciente import Paciente
from ..models.especialista import Especialista
from ..models.disponibilidad import Disponibilidad
from .utils.emails_utils import send_email_confirmation
from ..models.usuario import Usuario

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

@api.route('/delete/')
class DeleteCita(Resource):
    def delete(self):
        data = request.get_json()
        cita_id = int(data['cita_id'])
        cita = Cita.find_by_id(cita_id)

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


@api.route('/enlace')
class ConfirmarCitaCorreo(Resource):
    def post(self):
        data = request.get_json()
        cita_id = data['id_cita']

        if not cita_id:
            return {"message": "Falta el id_cita en el cuerpo de la solicitud", "success": False}, 400

        cita = Cita.get_by_id(cita_id)
        if not cita:
            return {"message": "No se encontró la cita", "success": False}, 404

        if cita.estado == "confirmada":
            return {"message": "La cita ya está confirmada", "success": True}, 200

        paciente = Paciente.find_by_id(cita.paciente_id)
        if not paciente:
            return {"message": "No se encontró el paciente asociado a la cita", "success": False}, 404

        usuario_info = Usuario.find_by_id(paciente.usuario_id)

        if not usuario_info:
            return {"message":"No se encontró el paciente asociado a la cita", "success": False}, 404

        try:
            send_email_confirmation(usuario_info.correo, usuario_info.primer_nombre, cita_id)
            return {"message": "Correo de confirmación enviado exitosamente", "success": True}, 200
        except Exception as e:
            return {"message": f"Error al enviar el correo: {str(e)}", "success": False}, 500

    @api.route('/confirmar_cita/<int:id_cita>')
    class ConfirmarCita(Resource):
        def get(self, id_cita):
            if not id_cita:
                abort(400, "Falta el id_cita en el cuerpo de la solicitud")

            cita = Cita.get_by_id(id_cita)
            if not cita:
                return {"message": "No se encontró la cita", "success": False}, 404

            if cita.estado == "confirmada":
                return {"message": "La cita ya está confirmada", "success": True}, 200

            cita.estado = "confirmada"
            cita.save()

            return {"message": "Cita confirmada exitosamente", "success": True}, 200

    @api.route('/<int:id_cita>')
    class Cita(Resource):
        def get(self, id_cita):
            if not id_cita:
                return {"message": "Falta el id_cita en el cuerpo de la solicitud", "success": False}, 400

            cita = Cita.get_by_id(id_cita)
            if not cita:
                return {"message": "No se encontró la cita", "success": False}, 404


            paciente_asociado = Paciente.find_by_id(cita.paciente_id)
            if not paciente_asociado:
                return {"message": "Paciente asociado no encontrado", "success": False}, 404
            usuario_asociado_paciente = Usuario.find_by_id(paciente_asociado.usuario_id)

            disponibilidad_asociada = Disponibilidad.find_by_id(cita.disponibilidad_id)
            if not disponibilidad_asociada:
                return {"message": "Disponibilidad asociada no encontrada", "success": False}, 404
            bloque_asociado = BloqueDeDisponibilidad.find_by_id(disponibilidad_asociada.bloque_id)

            especialista_asociado = Especialista.find_by_id(disponibilidad_asociada.especialista_id)
            if not especialista_asociado:
                return {"message": "Especialista asociado no encontrado", "success": False}, 404
            usuario_asociado_especialista = Usuario.find_by_id(especialista_asociado.usuario_id)
            especialidad = Especialidad.find_by_id(especialista_asociado.especialidad_id)

            info_cita = {
                "id_cita": id_cita,
                "paciente": f"{usuario_asociado_paciente.primer_nombre} {usuario_asociado_paciente.primer_apellido}",
                "rut_paciente": paciente_asociado.rut,
                "especialista": f"{usuario_asociado_especialista.primer_nombre} {usuario_asociado_especialista.primer_apellido}",
                "especialidad": especialidad.nombre,
                "tipo_cita": cita.tipo_cita,
                "detalle_cita": cita.detalles_adicionales,
                "estado_cita": cita.estado,
                "fecha": bloque_asociado.fecha.isoformat() if bloque_asociado.fecha else None,
                "hora_inicio": bloque_asociado.hora_inicio.isoformat() if bloque_asociado.hora_inicio else None,
                "hora_fin": bloque_asociado.hora_fin.isoformat() if bloque_asociado.hora_fin else None,
            }

            return info_cita, 200

    @api.route('/especialidad/<int:especialidad_id>')
    class MultiplesCitasPorEspecialidad(Resource):
        def get(self, especialidad_id):
            try:
                especialistas_asociados = Especialista.find_all_by_spiacialty(int(especialidad_id))

                if not especialistas_asociados:
                    return {'message': 'No se encontraron especialistas para esta especialidad.'}, 404

                especialistas_ids = [especialista.id for especialista in especialistas_asociados]

                disponibilidades = Disponibilidad.query.filter(
                    Disponibilidad.especialista_id.in_(especialistas_ids)
                ).all()

                if not disponibilidades:
                    return {'message': 'No se encontraron citas asociadas a esta especialidad.'}, 404

                disponibilidades_ids = [disponibilidad.id for disponibilidad in disponibilidades]

                citas = Cita.query.filter(Cita.disponibilidad_id.in_(disponibilidades_ids)).all()

                citas_data = [
                    {
                        'cita_id': cita.id,
                        'paciente_id': cita.paciente_id,
                        'disponibilidad_id': cita.disponibilidad_id,
                        'estado': cita.estado,
                        'tipo_cita': cita.tipo_cita,
                        'detalles_adicionales': cita.detalles_adicionales
                    } for cita in citas
                ]

                return {'citas': citas_data}, 200

            except SQLAlchemyError as e:
                return {'message': f'Error de base de datos: {str(e)}'}, 500
            except Exception as e:
                return {'message': f'Error al procesar la solicitud: {str(e)}'}, 500



