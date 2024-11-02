import os
from flask import Flask
from flask_restx import Api
from config.db_configs import set_db_configs, create_tables
from resources.ping import api as health_namespace
from resources.usuario import api as usuario_namespace

# Inicializar la aplicación Flask
app = Flask(__name__)

# Inicializar la API con Flask-RESTx
api = Api(app, version='1.0', title='API', description='API para proyecto')
api.add_namespace(health_namespace)
api.add_namespace(usuario_namespace)

# Configurar la base de datos
set_db_configs(app)
create_tables(app)

if __name__ == '__main__':
    app.run(debug=True)
