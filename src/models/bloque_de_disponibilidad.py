from src.config.db_configs import db
class BloqueDeDisponibilidad(db.Model):
    __tablename__ = 'bloque_de_disponibilidad'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    @classmethod
    def find_by_data(cls, _data):
        return cls.query.filter_by(fecha=_data['fecha'],
            hora_inicio=_data['hora_inicio'],
            hora_fin=_data['hora_fin']
            ).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def rollback(self):
        db.session.rollback()

