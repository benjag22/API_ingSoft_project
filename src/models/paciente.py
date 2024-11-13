from src.config.db_configs import db
import datetime

class Paciente(db.Model):
    __tablename__ = 'paciente'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    fecha_registro = db.Column(db.Date, default=datetime.datetime.utcnow)
    rut = db.Column(db.String(11), unique=True, nullable=False)

    @classmethod
    def find_by_rut(cls, rut):
        return cls.query.filter_by(rut=rut).first()

    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()
