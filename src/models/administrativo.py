from src.config.db_configs import db

class Administrativo(db.Model):
    __tablename__ = 'administrativo'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='SET NULL'))

    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).first()
