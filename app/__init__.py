
"""Recipe Box API — BE104."""

import os

from dotenv import load_dotenv
from flask import Flask, g, jsonify

from app.db import get_db
from app.routes.auth import auth_bp
from app.routes.recipes import recipes_bp


load_dotenv()


class Config:
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE = os.environ.get("RECIPES_DB_PATH")


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


def create_app(config_name="development"):
    app = Flask(__name__)

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }

    if config_name not in config_map:
        raise ValueError(
            f"Unknown config {config_name!r}. "
            f"Choose one of: {', '.join(config_map)}"
        )

    app.config.from_object(config_map[config_name])

    # Required JWT secret
    jwt_secret = os.environ.get("JWT_SECRET")

    if not jwt_secret:
        raise RuntimeError(
            "JWT_SECRET environment variable is required but missing"
        )

    app.config["JWT_SECRET"] = jwt_secret

    if not app.config.get("DATABASE"):
        raise RuntimeError(
            "RECIPES_DB_PATH environment variable is required but missing"
        )

    print("DEBUG from config:", app.config.get("DEBUG"))
    print("USING DB:", app.config.get("DATABASE"))

    # Register blueprints without changing existing URLs.
    app.register_blueprint(auth_bp, url_prefix="")
    app.register_blueprint(recipes_bp, url_prefix="")

    # Close the database connection after each application context.
    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)

        if db is not None:
            db.close()

    # Public route
    @app.get("/")
    def hello():
        return jsonify({
            "message": "Recipe Box API",
            "recipes": "/recipes",
        })

    return app