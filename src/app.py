from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from src.config.db_configs import set_db_configs,create_tables
from src.config.jwt_config import set_jwt_configs
from src.resources.ping import api as health_namespace
from src.resources.usuario import api as usuario_namespace
from src.resources.paciente import api as paciente_namespace
from src.resources.especialista import api as especialista_namespace
from src.resources.especialidad import api as especialidad_namespace
from src.resources.disponibilidad import api as disponibilidad_namespace
from src.resources.cita import api as cita_namespace
# Inicializar la API
app = Flask(__name__)
CORS(app)
# Inicializar la API con Flask-RESTx
api = Api(app, version='1.0', title='API', description='API para proyecto')
set_jwt_configs(app)

set_db_configs(app)
create_tables(app)

api.add_namespace(health_namespace)
api.add_namespace(usuario_namespace)
api.add_namespace(paciente_namespace)
api.add_namespace(especialista_namespace)
api.add_namespace(especialidad_namespace)
api.add_namespace(disponibilidad_namespace)
api.add_namespace(cita_namespace)


if __name__ == '__main__':
    app.run(debug=True)
