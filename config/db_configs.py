import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def set_db_configs(app):
    """
    función establece la URI de conexión a la base de datos PostgreSQL
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:.@localhost:5432/clinica'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)

def create_tables(app):
    with app.app_context():
        db.create_all()
