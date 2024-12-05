from src.config.db_configs import db

class Especialidad(db.Model):
    __tablename__ = 'especialidad'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    @classmethod
    def find_by_name(cls, _name):
        return cls.query.filter_by(nombre=_name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id = _id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()