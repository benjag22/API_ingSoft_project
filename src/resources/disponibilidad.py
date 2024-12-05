from flask import request, abort
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import SQLAlchemyError
from ..models.disponibilidad import Disponibilidad
from ..models.especialista import Especialista
from ..models.especialidad import Especialidad
from ..models.bloque_de_disponibilidad import BloqueDeDisponibilidad
from ..models.usuario import Usuario
from datetime import datetime

api = Namespace('disponibilidad', description='endpoints para disponibilidad de especialistas')

bloque_input = api.model(
    'BloqueDeDisponibilidad',
    {
        'fecha': fields.String(required=True, description='Fecha en formato YYYY-MM-DD'),
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

disponibilidad_output = api.model(
    'DisponibilidadOutput',
    {
        'id': fields.Integer(),
        'especialista_id': fields.Integer(),
        'bloque_id': fields.Integer()
    }
)

@api.route('/crear_multiples')
class CrearMultiplesDisponibilidad(Resource):
    @api.expect(api.model('ListaDeBloques', {
        'bloques': fields.List(fields.Nested(disponibilidad_input), required=True)
    }), validate=True)
    @api.marshal_list_with(disponibilidad_output)
    def post(self):
        data = request.get_json()
        bloques = data['bloques']
        disponibilidades = []

        for bloque in bloques:
            especialista_id = bloque['especialista_id']
            bloque_data = bloque['bloque']

            try:
                fecha = datetime.strptime(bloque_data['fecha'], '%Y-%m-%d').date()
                hora_inicio = datetime.strptime(bloque_data['hora_inicio'], '%H:%M').time()
                hora_fin = datetime.strptime(bloque_data['hora_fin'], '%H:%M').time()
            except ValueError:
                abort(400, "Formato de fecha u hora incorrecto")

            especialista = Especialista.query.get(especialista_id)
            if not especialista:
                abort(400, f"No se encontro un especialista con el ID {especialista_id}")

            bloque_existente = BloqueDeDisponibilidad.find_by_data({
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            })
            if not bloque_existente:
                bloque_existente = BloqueDeDisponibilidad(
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                try:
                    bloque_existente.save()
                except SQLAlchemyError:
                    bloque_existente.rollback()
                    abort(500, "Error al guardar el bloque")

            disponibilidad = Disponibilidad(
                especialista_id=especialista_id,
                bloque_id=bloque_existente.id
            )
            try:
                disponibilidad.save()
                disponibilidades.append(disponibilidad)
            except SQLAlchemyError:
                disponibilidad.rollback()
                abort(500, "Error al guardar la disponibilidad en la base de datos")

        return disponibilidades, 201

@api.route('/buscar/<int:especialistaId>')
class BuscarDisponibilidades(Resource):

    def get(self, especialistaId):
        especialista = Especialista.find_by_id(especialistaId)
        if not especialista:
            abort(400, f"No se encontró un especialista con el ID {especialistaId}")

        disponibilidades = Disponibilidad.get_all_by_especialista_id(especialistaId)
        if not disponibilidades:
            abort(404, 'no se encontraron disponibilidades')

        result=[]
        for disponibilidad in disponibilidades:
            if not disponibilidad.ocupada:
                bloque = BloqueDeDisponibilidad.find_by_id(disponibilidad.bloque_id)
                result.append({
                    'id': disponibilidad.id,
                    'especialista_id': disponibilidad.especialista_id,
                    'fecha': bloque.fecha.strftime('%Y-%m-%d'),
                    'hora_inicio': bloque.hora_inicio.strftime('%H:%M:%S') if bloque.hora_inicio else None,
                    'hora_fin': bloque.hora_fin.strftime('%H:%M:%S') if bloque.hora_fin else None
                })
        return {'disponibilidades': result},200

disponibilidad_output_for_pacient= api.model('Disponibilidad para pacientes',
    {
        'especialidad_id': fields.Integer(requierd_key=True, description ="id de la especialidad"),
        'especialidad': fields.String(required=True, description="especialidad"),
        'nombre_especialista': fields.String(required=True, description="nombre del especialista"),
        'apellido_especialista': fields.String(required=True, description="apellido del especialista"),
        'fecha': fields.String(required=True, description='Fecha en formato YYYY-MM-DD'),
        'hora_inicio': fields.String(required=True, description="Hora de inicio en formato HH:MM"),
        'hora_fin': fields.String(required=True, description="Hora de fin en formato HH:MM")
        }
)
disponibilidades_output_for_pacient= api.model('Disponibilidades para pacientes',
                                               {'disponibilidades':[disponibilidad_output_for_pacient]})
@api.route('/obtener-disponibilidades')
class ObtenerDisponibilidad(Resource):
    def get(self):
        disponibilidades = Disponibilidad.get_all()
        if not disponibilidades:
            abort(404, "no se encontraron disponibiladades")

        result=[]
        for disponibilidad in disponibilidades:
            if not disponibilidad.ocupada:
                especialista = Especialista.find_by_id(disponibilidad.especialista_id)
                especialista_info = Usuario.find_by_id(especialista.usuario_id)
                especialidad = Especialidad.find_by_id(especialista.especialidad_id)
                bloque = BloqueDeDisponibilidad.find_by_id(disponibilidad.bloque_id)
                result.append({
                    'disponibilidad_id': disponibilidad.id,
                    'especialidad_id': especialidad.id,
                    'especialidad': especialidad.nombre,
                    'nombre_especialista': especialista_info.primer_nombre,
                    'apellido_especialista': especialista_info.primer_apellido,
                    'correo':especialista_info.correo,
                    'fecha': bloque.fecha.strftime('%Y-%m-%d'),
                    'hora_inicio': bloque.hora_inicio.strftime('%H:%M:%S') if bloque.hora_inicio else None,
                    'hora_fin': bloque.hora_fin.strftime('%H:%M:%S') if bloque.hora_fin else None
                })

        return result,200
disponibilidades_delete_input = api.model(
    'Disponibilidad',
    {
        'especialista_id': fields.Integer(required=True, description="ID del especialista"),
    }
)
########
@api.route('/<int:especialidad_id>', defaults={'specialist_name': None})
@api.route('/<int:especialidad_id>')
@api.route('/obtener-disponibilidades')
class MultiplesDisponibilidadesPorEspecialidad(Resource):
    def get(self, especialidad_id):
        try:
            # Obtener los especialistas de la especialidad solicitada
            especialistas_asociados = Especialista.find_all_by_spiacialty(int(especialidad_id))

            if not especialistas_asociados:
                return {'message': 'No se encontraron especialistas para esta especialidad.'}, 404

            # Obtener las disponibilidades de la especialidad solicitada
            disponibilidad_asociada = Disponibilidad.find_all_by_spiacialty(int(especialidad_id))

            result = []
            for disponibilidad in disponibilidad_asociada:
                if not disponibilidad.ocupada:
                    especialista = Especialista.find_by_id(disponibilidad.especialista_id)
                    especialista_info = Usuario.find_by_id(especialista.usuario_id)
                    especialidad = Especialidad.find_by_id(especialista.especialidad_id)
                    bloque = BloqueDeDisponibilidad.find_by_id(disponibilidad.bloque_id)
                    result.append({
                        'disponibilidad_id': disponibilidad.id,
                        'especialidad_id': especialidad.id,
                        'especialidad': especialidad.nombre,
                        'nombre_especialista': especialista_info.primer_nombre,
                        'apellido_especialista': especialista_info.primer_apellido,
                        'correo': especialista_info.correo,
                        'fecha': bloque.fecha.strftime('%Y-%m-%d'),
                        'hora_inicio': bloque.hora_inicio.strftime('%H:%M:%S') if bloque.hora_inicio else None,
                        'hora_fin': bloque.hora_fin.strftime('%H:%M:%S') if bloque.hora_fin else None
                    })
                result.append(result.append)

        except SQLAlchemyError as e:
            return {'message': f'Error de base de datos: {str(e)}'}, 500
        except Exception as e:
            return {'message': f'Error al procesar la solicitud: {str(e)}'}, 500

@api.route('/<int:especialidad_id>', defaults={'specialist_name': None})
@api.route('/<string:specialist_name>/<int:especialidad_id>')
@api.route('/obtener-disponibilidades')
class MultiplesDisponibilidadesPorNombre(Resource):
    def get(self, especialidad_id, specialist_name):
        try:
            # Obtener los especialistas de la especialidad solicitada
            especialistas_asociados = Especialista.find_all_by_spiacialty(int(especialidad_id))

            if not especialistas_asociados:
                return {'message': 'No se encontraron especialistas para esta especialidad.'}, 404

            especialistas_ids = []
            for especialista in especialistas_asociados:
                usuario_asociado_especialista = Usuario.find_by_id(especialista.usuario_id)
                if not usuario_asociado_especialista:
                    continue

                if specialist_name:
                    nombre_completo = f"{usuario_asociado_especialista.primer_nombre} {usuario_asociado_especialista.primer_apellido}".lower()
                    if specialist_name.lower() not in nombre_completo:
                        continue

                especialistas_ids.append(especialista.id)

            # Obtener las disponibilidades de la especialidad solicitada
            disponibilidad_asociada = Disponibilidad.find_all_by_spiacialty(especialistas_ids)

            result = []
            for disponibilidad in disponibilidad_asociada:
                if not disponibilidad.ocupada:
                    especialista = Especialista.find_by_id(disponibilidad.especialista_id)
                    especialista_info = Usuario.find_by_id(especialista.usuario_id)
                    especialidad = Especialidad.find_by_id(especialista.especialidad_id)
                    bloque = BloqueDeDisponibilidad.find_by_id(disponibilidad.bloque_id)
                    result.append({
                        'disponibilidad_id': disponibilidad.id,
                        'especialidad_id': especialidad.id,
                        'especialidad': especialidad.nombre,
                        'nombre_especialista': especialista_info.primer_nombre,
                        'apellido_especialista': especialista_info.primer_apellido,
                        'correo': especialista_info.correo,
                        'fecha': bloque.fecha.strftime('%Y-%m-%d'),
                        'hora_inicio': bloque.hora_inicio.strftime('%H:%M:%S') if bloque.hora_inicio else None,
                        'hora_fin': bloque.hora_fin.strftime('%H:%M:%S') if bloque.hora_fin else None
                    })
                result.append(result.append)

        except SQLAlchemyError as e:
            return {'message': f'Error de base de datos: {str(e)}'}, 500
        except Exception as e:
            return {'message': f'Error al procesar la solicitud: {str(e)}'}, 500
########

@api.route('/eliminar/<int:id>')
class EliminarDisponibilidad(Resource):
    @api.expect(disponibilidades_delete_input)
    def delete(self, id):
        try:
            disponibilidad = Disponibilidad.find_by_id(id)
            if not disponibilidad:
                return {"message": f"No se encontró la disponibilidad con ID {id}"}, 404

            disponibilidad.delete()

            return {"message": f"Disponibilidad con ID {id} eliminada exitosamente."}, 200

        except Exception as e:
            return {"message": f"Error al eliminar la disponibilidad: {str(e)}"}, 500