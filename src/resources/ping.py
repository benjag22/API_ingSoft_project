from flask_restx import Resource, Namespace

# Definir el namespace para el estado de salud
# endpoint /ping
api = Namespace('ping', description='Estado de la api(200)')

@api.route('/')
class HealthStatus(Resource):
    def get(self) -> dict:
        return {'status': 'ok'}
