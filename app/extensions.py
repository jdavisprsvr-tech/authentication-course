from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # add this

db = SQLAlchemy()
migrate = Migrate()  # add this
db = SQLAlchemy()