from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from config.db_configs import set_db_configs, create_tables
from config.jwt_config import set_jwt_configs
from resources.ping import api as health_namespace
from resources.usuario import api as usuario_namespace
from resources.paciente import api as paciente_namespace
# Inicializar la API
app = Flask(__name__)
CORS(app)
# Inicializar la API con Flask-RESTx
api = Api(app, version='1.0', title='API', description='API para proyecto')
set_jwt_configs(app)
api.add_namespace(health_namespace)
api.add_namespace(usuario_namespace)
api.add_namespace(paciente_namespace)

# Configurar la base de datos
set_db_configs(app)
create_tables(app)

if __name__ == '__main__':
    app.run(debug=True)
