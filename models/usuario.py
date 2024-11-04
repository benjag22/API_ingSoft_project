from config.db_configs import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    primer_nombre = db.Column(db.String(50), nullable=False)
    primer_apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasenia = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(correo=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()
