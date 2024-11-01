from flask import request, abort, jsonify
from flask_restx import Namespace, Resource, fields
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token
from models.usuario import Usuario
from models.paciente import Paciente
import datetime

api = Namespace('paciente', description='endpoints para pacientes')

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
        )
    }
)
paciente_input = api.model(
    'PacienteRegisterFields',
    {
        'rut': fields.String(required=True),
        'usuario': fields.Nested(user_input, required=True)
    }
)
paciente_output = api.inherit(
    'PacienteSalida',
    {
        'id': fields.Integer(required=True),
        'usuario_id': fields.Integer(required=True),
        'fecha_registro': fields.DateTime(required=True),
        'rut': fields.String(required=True),
    }
)

@api.route('/registrar')
@api.doc(
    responses={
        404: 'Paciente no encontrado',
        400: 'Bad request',
        409: 'Paciente ya registrado',
        500: 'Ha ocurrido un error mientras se crea el apciente(error de server)'
    }
)
class RegisterPaciente(Resource):
    @api.expect(paciente_input, validate=True)
    @api.marshal_with(paciente_output)
    def post(self):
        data = request.get_json()
        usuario_data = data['usuario']
        rut = data['rut']

        # Verificar si el RUT ya está registrado
        paciente_existe = Paciente.find_by_rut(rut)
        if paciente_existe:
            abort(409, 'Paciente ya registrado con este RUT.')

        # Verificar si el usuario ya existe por correo
        usuario = Usuario.find_by_email(usuario_data['correo'])

        if not usuario:
            # Crear un nuevo usuario si no existe
            usuario = Usuario(
                primer_nombre=usuario_data['primer_nombre'],
                primer_apellido=usuario_data['primer_apellido'],
                correo=usuario_data['correo'],
                contrasenia=pbkdf2_sha256.hash(usuario_data['contrasenia']),
                tipo=usuario_data['tipo']
            )
            try:
                usuario.save()
            except SQLAlchemyError as e:
                abort(500, 'Error al guardar el usuario en la base de datos.')

        # Crear el paciente asociado
        nuevo_paciente = Paciente(
            usuario_id=usuario.id,
            fecha_registro=datetime.datetime.now(),
            rut=rut
        )
        try:
            nuevo_paciente.save()
        except SQLAlchemyError as e:
            abort(500, 'Error al guardar el paciente en la base de datos.')

        # Generar y retornar token de acceso
        access_token = create_access_token(identity={'id': usuario.id, 'tipo': usuario.tipo})

        return {
            'paciente': nuevo_paciente,
            'access_token': access_token
        }, 201