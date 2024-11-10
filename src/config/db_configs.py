from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def set_db_configs(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:.@localhost:5432/clinica'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)  # Asegúrate de que esta línea esté presente y se ejecute

def create_tables(app):
    with app.app_context():
        db.create_all()