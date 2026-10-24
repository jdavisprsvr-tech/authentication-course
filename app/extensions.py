from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # add this
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()  # add this
cache = Cache()