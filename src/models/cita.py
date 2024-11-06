from src.config.db_configs import db

class Cita(db.Model):
    __tablename__ = 'cita'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id', ondelete='CASCADE'), nullable=False)
    disponibilidad_id = db.Column(db.Integer, db.ForeignKey('disponibilidad.id', ondelete='CASCADE'), nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='por_confirmar',
                       check_constraint="estado IN ('por_confirmar', 'confirmada', 'cancelada', 'completada')")
    tipo_cita = db.Column(db.String(100))
    detalles_adicionales = db.Column(db.Text)
