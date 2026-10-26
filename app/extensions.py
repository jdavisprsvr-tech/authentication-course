from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # add this
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()  # add this
cache = Cache()
limiter = Limiter(key_func=get_remote_address)