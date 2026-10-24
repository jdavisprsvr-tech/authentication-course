

"""Recipe Box API — BE104."""

import os

from dotenv import load_dotenv
from flask import Flask
from app.routes.auth import auth_bp
from app.routes.recipes import recipes_bp
from app.extensions import db, migrate, cache

load_dotenv()


class Config:
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE = os.path.abspath(
        os.environ.get("RECIPES_DB_PATH") or "recipes.db"
    )
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.path.abspath("recipes_test.db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE


class ProductionConfig(Config):
    pass


def create_app(config_name="development"):
    app = Flask(__name__)

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    if config_name not in config_map:
        raise ValueError(
            f"Unknown config {config_name!r}. "
            f"Choose one of: {', '.join(config_map)}"
        )

    app.config.from_object(config_map[config_name])
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    jwt_secret = os.environ.get("JWT_SECRET")

    if not jwt_secret:
        raise RuntimeError(
            "JWT_SECRET environment variable is required but missing"
        )

    app.config["JWT_SECRET"] = jwt_secret

    print("DEBUG from config:", app.config.get("DEBUG"))
    print("USING DB:", app.config.get("DATABASE"))

    app.register_blueprint(auth_bp, url_prefix="")
    app.register_blueprint(recipes_bp, url_prefix="")

    return app
