from flask import request, abort, jsonify
from flask_restx import Namespace, Resource, fields
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token
from models.usuario import Usuario
from models.especialista import Especialista
import datetime

api = Namespace('especialista', description='endpoints para especialistas')

user_input = api.model(
    'UserRegisterFields',
    {
        'primer_nombre': fields.String(required=True),
        'primer_apellido': fields.String(required=True),
        'correo': fields.String(required=True),
        'contrasenia': fields.String(required=True),
        'tipo': fields.String(
            required=True,
            description="Tipo de usuario: administrativo, especialista, o paciente",
            enum=['administrativo', 'especialista', 'paciente']
        ),
        'nombre_usuario': fields.String(required=True)
    }
)
especialista_input = api.model(
    'EspecialistaRegisterFields',
    {
        'especialidad_id': fields.Integer(required=True),
        'usuario': fields.Nested(user_input, required=True)
    }
)
especialista_output = api.inherit(
    'EspecialistaSalida',
    {
        'id': fields.Integer(required=True),
        'usuario_id': fields.Integer(required=True),
        'especialidad_id': fields.Integer(required=True),
    }
)


@api.route('/registrar')
@api.doc(
    responses={
        400: 'Bad request',
        409: 'Especialista ya registrado',
        500: 'Ha ocurrido un error mientras se crea el especialista (error de servidor)'
    }
)
class RegisterEspecialista(Resource):
    @api.expect(especialista_input, validate=True)
    @api.marshal_with(especialista_output)
    def post(self):
        data = request.get_json()
        usuario_data = data['usuario']
        especialidad_id = data['especialidad_id'].strip().capitalize()

        # Verificar si el usuario ya existe por correo
        usuario = Usuario.find_by_email(usuario_data['correo'])

        if not usuario:
            # Crear un nuevo usuario si no existe
            usuario = Usuario(
                primer_nombre=usuario_data['primer_nombre'],
                primer_apellido=usuario_data['primer_apellido'],
                correo=usuario_data['correo'],
                contrasenia=pbkdf2_sha256.hash(usuario_data['contrasenia']),
                tipo=usuario_data['tipo'],
                nombre_usuario=usuario_data['nombre_usuario']
            )
            try:
                usuario.save()
            except SQLAlchemyError as e:
                abort(500, 'Error al guardar el usuario en la base de datos.')

        # Crear el especialista asociado
        nuevo_especialista = Especialista(
            usuario_id=usuario.id,
            especialidad_id=especialidad_id
        )
        try:
            nuevo_especialista.save()
        except SQLAlchemyError as e:
            abort(500, 'Error al guardar el especialista en la base de datos.')

        # Generar y retornar token de acceso
        access_token = create_access_token(identity={'id': usuario.id, 'tipo': usuario.tipo})

        return {
            'especialista': nuevo_especialista,
            'access_token': access_token
        }, 201