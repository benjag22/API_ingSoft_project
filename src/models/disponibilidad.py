from email.policy import default

from src.config.db_configs import db


class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad'

    id = db.Column(db.Integer, primary_key=True)
    especialista_id = db.Column(db.Integer, db.ForeignKey('especialista.id', ondelete='CASCADE'), nullable=False)
    bloque_id = db.Column(db.Integer, db.ForeignKey('bloque_de_disponibilidad.id', ondelete='CASCADE'), nullable=False)
    ocupada = db.Column(db.Boolean, default=False, nullable=False)


    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all_by_especialista_id(self, _especialista_id):
        return Disponibilidad.query.filter_by(especialista_id=_especialista_id).all()

    @classmethod
    def find_by_id(self, _id):
        return Disponibilidad.query.filter_by(id=_id).first()

    @classmethod
    def get_all(cls):
        return Disponibilidad.query.all()

