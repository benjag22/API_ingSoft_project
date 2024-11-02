from config.db_configs import db
import datetime

class Paciente(db.Model):
    __tablename__ = 'paciente'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    fecha_registro = db.Column(db.Date, default=datetime)
    rut = db.Column(db.String(11), unique=True, nullable=False)

    # Relationships
    usuario = db.relationship('Usuario', back_populates='paciente')
    citas = db.relationship('Cita', back_populates='paciente')

    @classmethod
    def find_by_rut(cls, rut):
        return cls.query.filter_by(rut=rut).first()

    def save(self):
        db.session.add(self)
        db.session.commit()