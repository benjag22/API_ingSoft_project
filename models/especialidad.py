from config.db_configs import db

class Especialidad(db.Model):
    __tablename__ = 'especialidad'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
