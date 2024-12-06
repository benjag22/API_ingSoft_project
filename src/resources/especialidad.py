from flask import request, abort
from flask_restx import Namespace, Resource, fields
from ..models.especialidad import Especialidad
from sqlalchemy.exc import SQLAlchemyError

api = Namespace('especialidades', description='Endpoints para gestionar especialidades')
especialidad_input = api.model(
    'EspecialidadInput',
    {
        'nombre': fields.String(required=True, description="Nombre de la especialidad", max_length=100)
    }
)

especialidad_output = api.inherit(
    'EspecialidadOutput',
    {
        'id': fields.Integer(required=True),
        'nombre': fields.String(required=True),
    }
)
@api.route('/registrar')
class CreateEspecialidad(Resource):
    @api.expect(especialidad_input, validate=True)
    @api.marshal_with(especialidad_output)
    def post(self):

        data = request.get_json()
        if Especialidad.find_by_name(data['nombre']):
            abort(409, 'La especialidad ya existe.')
        nueva_especialidad = Especialidad(nombre=data['nombre'])
        try:
            nueva_especialidad.save()
        except SQLAlchemyError:
            abort(500, 'Error al guardar la especialidad en la base de datos.')
        return nueva_especialidad, 201


@api.route('')
class Especialidades(Resource):
    def get(self):
        try:
            especialidades = Especialidad.find_all()
            if not especialidades:
                abort(404, "No se encontraron especialidades.")

            result = []
            for especialidad in especialidades:
                result.append({
                    "id": especialidad.id,
                    "nombre": especialidad.nombre
                })

            return result, 200  

        except SQLAlchemyError as e:
            abort(500, f"Error en la base de datos: {str(e)}")
        except Exception as e:
            abort(500, f"Error inesperado: {str(e)}")
