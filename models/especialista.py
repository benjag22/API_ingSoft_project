from config.db_configs import db

class Especialista(db.Model):
    __tablename__ = 'especialista'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='SET NULL'))
