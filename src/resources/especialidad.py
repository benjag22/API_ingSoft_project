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