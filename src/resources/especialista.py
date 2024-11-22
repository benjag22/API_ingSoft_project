from flask import request, abort
from flask_restx import Namespace, Resource, fields
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from ..models.usuario import Usuario
from ..models.especialidad import Especialidad
from ..models.especialista import Especialista

api = Namespace('especialistas', description='endpoints para especialistas')

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
        'especialidad': fields.String(required=True),
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

        usuario = Usuario.find_by_email(usuario_data['correo'])
        tipo_usuario = usuario_data['tipo']

        if not usuario and tipo_usuario == 'especialista':
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
        nuevo_especialista = Especialista(
            usuario_id=usuario.id,
            especialidad_id=especialidad.id
        )
        try:
            nuevo_especialista.save()
        except SQLAlchemyError:
            abort(500, 'Error al guardar el especialista en la base de datos.')

        # Generar y retornar token de acceso
        return {
            'id': nuevo_especialista.id,
            'usuario_id': nuevo_especialista.usuario_id,
            'especialidad_id': nuevo_especialista.especialidad_id
        }, 201

    @api.route('/por_correo/<string:correo>')
    @api.doc(
        responses={
            200: 'Especialista encontrado',
            404: 'Especialista no encontrado',
            500: 'Error en el servidor'
        }
    )
    class EspecialistaPorCorreo(Resource):
        def get(self, correo):
            usuario_de_especialista = Usuario.find_by_email(correo)
            if not usuario_de_especialista:
                abort(404, "no se encontro el usuario asciado")

            especialista = Especialista.find_by_usuario_id(usuario_de_especialista.id)
            if not especialista:
                abort(404, 'Especialista no encontrado')

            return {
                'id': especialista.id,
                'usuario_id': especialista.usuario_id,
                'especialidad_id': especialista.especialidad_id
            }

    especialista_por_especialidad_output = api.inherit(
        'EspecialistasField',
        {
            'nombre_especialidad': fields.Integer(required=True),
            'especialidad_id': fields.Integer(required=True),
        }
    )

    @api.route('/<string:especialidad>')
    @api.doc(
        responses={
            200: 'Especialista encontrado',
            404: 'Especialista no encontrado',
            500: 'Error en el servidor'
        }
    )
    class EspecialistasDeEspecialidad(Resource):
        @api.marshal_with(especialista_output)
        def get(self, especialidad):
            try:
                if especialidad.isdigit():
                    #caso de que se busque por id de la especialidad
                    especialidad_id = int(especialidad)
                else:
                    #Caso de que se busque por nombre
                    especialidad_obj = Especialidad.find_by_name(especialidad)
                    if not especialidad_obj:
                        abort(404, 'Especialidad no encontrada')
                    especialidad_id = especialidad_obj.id

                especialistas = Especialista.find_all_by_spiacialty(especialidad_id)


                if not especialistas:
                    abort(404, 'Especialistas no encontrado')

                return especialistas, 200
            except Exception as e:
                abort(500,"error")


