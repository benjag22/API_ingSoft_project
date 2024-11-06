from flask import request, abort
from flask_restx import Namespace, Resource, fields
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token
from src.models.usuario import Usuario

api = Namespace('usuarios', description='endpoints para usuarios')

# Modelos de entrada de datos
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
        'nombre_usuario': fields.String(required=True),
    }
)

login_input = api.model(
    'LoginFields',
    {
        'correo': fields.String(required=True),
        'contrasenia': fields.String(required=True)
    }
)

user_output = api.model(
    'UserOutput',
    {
        'id': fields.Integer(),
        'primer_nombre': fields.String(),
        'primer_apellido': fields.String(),
        'correo': fields.String(),
        'tipo': fields.String()
    }
)


# Endpoint para registro de usuario
@api.route('/registrar')
@api.doc(
    responses={
        400: 'Bad Request',
        500: 'An error occurred while registering user'
    }
)
class Register(Resource):
    @api.expect(user_input, validate=True)
    @api.marshal_with(user_output)
    def post(self):
        user_data = request.get_json()

        # Verificar si el correo ya está registrado
        existing_user = Usuario.find_by_email(user_data['correo'])
        if existing_user:
            abort(400, 'Correo ya registrado. Por favor, inicia sesión.')

        # Crear un nuevo usuario
        usuario = Usuario(
            primer_nombre=user_data['primer_nombre'],
            primer_apellido=user_data['primer_apellido'],
            correo=user_data['correo'],
            contrasenia=pbkdf2_sha256.hash(user_data['contrasenia']),
            tipo=user_data['tipo'],
            nombre_usuario=user_data['nombre_usuario']
        )

        # Guardar usuario en la base de datos
        try:
            usuario.save()
        except SQLAlchemyError as e:
            abort(500, 'Ocurrió un error mientras se creaba el usuario.')

        return usuario, 201


# Endpoint para login de usuario
@api.route('/login')
@api.doc(
    responses={
        404: 'User not found',
        400: 'Bad request',
        500: 'An error occurred while logging in'
    }
)
class UserLogin(Resource):
    @api.expect(login_input, validate=True)
    def post(self):
        user_data = request.get_json()
        email = user_data['correo']
        password = user_data['contrasenia']

        # Verificar que se haya proporcionado el email y contraseña
        if not email or not password:
            abort(400, 'Por favor proporciona el correo y la contraseña.')

        # Buscar el usuario por correo
        usuario = Usuario.find_by_email(email)
        if not usuario:
            abort(404, f'Usuario no existe con el correo {email}.')

        # Verificar la contraseña
        is_password_correct = pbkdf2_sha256.verify(password, usuario.contrasenia)
        if not is_password_correct:
            abort(401, 'Contraseña incorrecta.')

        # Crear token de acceso con el ID y tipo de usuario
        access_token = create_access_token(identity={'id': usuario.id, 'tipo': usuario.tipo})
        return {'access_token': access_token, 'tipo': usuario.tipo}, 200
