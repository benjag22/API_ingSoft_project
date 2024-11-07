from flask import request, abort
from flask_restx import Namespace, Resource, fields
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from ..models.usuario import Usuario
from ..models.especialidad import Especialidad
from ..models.administrativo import Administrativo

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
administrativo_input = api.model(
    'EspecialistaRegisterFields',
    {
        'especialidad': fields.String(required=True),
        'usuario': fields.Nested(user_input, required=True)
    }
)
administrativo_output = api.inherit(
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
        409: 'Administrativo ya registrado',
        500: 'Ha ocurrido un error mientras se crea el administrativo (error de servidor)'
    }
)
class RegisterAdministrativo(Resource):
    @api.expect(administrativo_input, validate=True)
    @api.marshal_with(administrativo_output)
    def post(self):

        data = request.get_json()
        usuario_data = data['usuario']

        # Verificar si el usuario ya existe por correo
        usuario = Usuario.find_by_email(usuario_data['correo'])
        tipo_usuario = usuario_data['tipo']

        if not usuario and tipo_usuario == 'administrativo':
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

        especialidad_nombre = data['especialidad'].strip().lower()

        especialidad = Especialidad.find_by_name(especialidad_nombre)
        if not especialidad:
            especialidad = Especialidad(nombre=especialidad_nombre)
            try:
                especialidad.save()
            except SQLAlchemyError:
                abort(500, 'Error al guardar la especialidad en la base de datos.')

        # Crear el especialista asociado
        nuevo_administrativo = Administrativo(
            usuario_id=usuario.id,
            especialidad_id=especialidad.id
        )
        try:
            nuevo_administrativo.save()
        except SQLAlchemyError:
            abort(500, 'Error al guardar el administrativo en la base de datos.')

        # Generar y retornar token de acceso
        return {
            'id': nuevo_administrativo.id,
            'usuario_id': nuevo_administrativo.usuario_id,
            'especialidad_id': nuevo_administrativo.especialidad_id
        }, 201