from config.db_configs import db

class Administrativo(db.Model):
    __tablename__ = 'administrativo'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='SET NULL'))

    # Relationships
    usuario = db.relationship('Usuario', back_populates='administrativo')
    especialidad = db.relationship('Especialidad', back_populates='administrativos')