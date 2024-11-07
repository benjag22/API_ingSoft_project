from src.config.db_configs import db


class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad'

    id = db.Column(db.Integer, primary_key=True)
    especialista_id = db.Column(db.Integer, db.ForeignKey('especialista.id', ondelete='CASCADE'), nullable=False)
    bloque_id = db.Column(db.Integer, db.ForeignKey('bloque_de_disponibilidad.id', ondelete='CASCADE'), nullable=False)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('especialista_id', 'bloque_id', name='unique_especialista_bloque'),
    )

    def save(self):
        db.session.add(self)
        db.session.commit()