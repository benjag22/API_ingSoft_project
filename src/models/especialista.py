from src.config.db_configs import db

class Especialista(db.Model):
    __tablename__ = 'especialista'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='SET NULL'))

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_usuario_id(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).first()
    @classmethod
    def find_all_by_spiacialty(cls,_id_especialidad):
        return cls.query.filter_by(especialidad_id=_id_especialidad).all()

    def save(self):
        db.session.add(self)
        db.session.commit()
