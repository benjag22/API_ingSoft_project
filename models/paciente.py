from config.db_configs import db

class BloqueDeDisponibilidad(db.Model):
    __tablename__ = 'bloque_de_disponibilidad'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.CheckConstraint("EXTRACT(EPOCH FROM hora_fin) - EXTRACT(EPOCH FROM hora_inicio) = 2700",
                           name="duracion_bloque"),
    )

    # Relationships
    disponibilidades = db.relationship('Disponibilidad', back_populates='bloque')
