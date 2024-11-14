from src.config.db_configs import db

class Cita(db.Model):
    __tablename__ = 'cita'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id', ondelete='CASCADE'), nullable=False)
    disponibilidad_id = db.Column(db.Integer, db.ForeignKey('disponibilidad.id', ondelete='CASCADE'), nullable=False)
    estado = db.Column(db.String(20), default='por_confirmar')
    tipo_cita = db.Column(db.String(100))
    detalles_adicionales = db.Column(db.Text)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)