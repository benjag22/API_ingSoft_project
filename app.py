import models
from config.db_configs import set_db_configs, create_tables
from flask import Flask
app = Flask(__name__)
set_db_configs(app)
create_tables(app)
if __name__ == '__main__':
    app.run(debug=True)
