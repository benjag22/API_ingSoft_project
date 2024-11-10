from flask import request, abort
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import SQLAlchemyError
from ..models.bloque_de_disponibilidad import BloqueDeDisponibilidad
from ..models.disponibilidad import Disponibilidad
from ..models.especialista import Especialista
from .utils.my_date_format import MyDateFormat
from datetime import datetime, timedelta

api = Namespace('disponibilidad', description='endpoints para disponibilidad de especialistas')

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

disponibilidad_output = api.model(
    'DisponibilidadOutput',
    {
        'id': fields.Integer(),
        'especialista_id': fields.Integer(),
        'bloque_id': fields.Integer()
    }
)

@api.route('/crear')
class CrearDisponibilidad(Resource):
    @api.expect(disponibilidad_input, validate=True)
    @api.marshal_with(disponibilidad_output)
    def post(self):
        data = request.get_json()

        especialista_id = data['especialista_id']
        bloque_data = data['bloque']

        fecha = datetime.strptime(bloque_data['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(bloque_data['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(bloque_data['hora_fin'], '%H:%M').time()

        especialista = Especialista.query.get(especialista_id)
        if not especialista:
            abort(400, f"No se encontró un especialista con el ID {especialista_id}")

        data=[fecha,hora_inicio,hora_fin]
        bloque = BloqueDeDisponibilidad.find_by_data(data)
        duracion = datetime.combine(fecha, hora_fin) - datetime.combine(fecha, hora_inicio)

        if not bloque and duracion == timedelta(minutes=45):

            bloque = BloqueDeDisponibilidad(
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            try:
                bloque.save()
            except SQLAlchemyError:
                bloque.rollback()
                abort(500, "Error al guardar el bloque de disponibilidad en la base de datos")

        disponibilidad = Disponibilidad(
            especialista_id=especialista_id,
            bloque_id=bloque.id
        )

        try:
            disponibilidad.save()
        except SQLAlchemyError:
            disponibilidad.rollback()
            abort(500, "Error al guardar la disponibilidad en la base de datos")

        return disponibilidad, 201

@api.route('/buscar/<int:especialista_id>')
class BuscarDisponibilidades(Resource):

    def get(self, especialista_id):
        especialista = Especialista.find_by_id(especialista_id)
        if not especialista:
            abort(400, f"No se encontró un especialista con el ID {especialista_id}")

        disponibilidades = Disponibilidad.get_by_especialista_id(especialista_id)
        if not disponibilidades:
            abort(404, 'no se encontraron disponibilidades')

        result=[]
        for disponibilidad in disponibilidades:
            bloque = BloqueDeDisponibilidad.find_by_id(disponibilidad.bloque_id)
            result.append({
                'id': disponibilidad.id,
                'especialista_id': disponibilidad.especialista_id,
                'fecha': bloque.fecha,
                'hora_inicio': bloque.hora_inicio,
                'hora_fin': bloque.hora_fin
            })

        return {'disponibilidades': result},200



