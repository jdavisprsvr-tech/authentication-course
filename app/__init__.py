
"""Recipe Box API — BE104."""

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from jwt import ExpiredSignatureError, PyJWTError
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256")


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET")

    DATABASE = "recipes.db"

    # Database helpers
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # Authentication decorator
    def token_required(view_function):
        @wraps(view_function)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"error": "token is required"}), 401

            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({
                    "error": "invalid authorization header"
                }), 401

            token = parts[1]
            secret = app.config.get("JWT_SECRET")

            if not secret:
                app.logger.error("JWT_SECRET is not configured")
                return jsonify({
                    "error": "server configuration error"
                }), 500

            try:
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=["HS256"],
                )
                user_id = int(payload["sub"])

            except ExpiredSignatureError:
                return jsonify({
                    "error": "token has expired, please log in again"
                }), 401

            except (PyJWTError, KeyError, TypeError, ValueError):
                return jsonify({"error": "invalid token"}), 401

            user = get_db().execute(
                "SELECT id, username, role FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

            if user is None:
                return jsonify({"error": "invalid token"}), 401

            g.current_user = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            }

            return view_function(*args, **kwargs)

        return decorated

    # Public routes
    @app.get("/")
    def hello():
        return jsonify({
            "message": "Recipe Box API",
            "recipes": "/recipes",
        })

    @app.get("/recipes")
    def list_recipes():
        rows = get_db().execute(
            "SELECT * FROM recipes ORDER BY id"
        ).fetchall()

        return jsonify([recipe_to_dict(row) for row in rows])

    @app.get("/recipes/<int:recipe_id>")
    def get_recipe(recipe_id):
        row = get_db().execute(
            "SELECT * FROM recipes WHERE id = ?",
            (recipe_id,),
        ).fetchone()

        if row is None:
            return jsonify({"error": "recipe not found"}), 404

        return jsonify(recipe_to_dict(row))

    # Recipe creation
    @app.post("/recipes")
    @token_required
    def create_recipe():
        user_id = g.current_user["id"]
        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({"error": "a JSON body is required"}), 400

        required = ("title", "ingredients", "instructions")

        for field in required:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        is_public = 1 if data.get("is_public", False) else 0
        db = get_db()

        try:
            cur = db.execute(
                """
                INSERT INTO recipes
                (title, ingredients, instructions, is_public, owner_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data["ingredients"],
                    data["instructions"],
                    is_public,
                    user_id,
                ),
            )
            db.commit()

        except sqlite3.IntegrityError:
            return jsonify({
                "error": "a recipe with that title already exists"
            }), 409

        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()

        return jsonify(recipe_to_dict(row)), 201

    # Recipe updates
    @app.patch("/recipes/<int:recipe_id>")
    @token_required
    def update_recipe(recipe_id):
        user_id = g.current_user["id"]
        role = g.current_user["role"]
        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({"error": "a JSON body is required"}), 400

        fields = []
        values = []

        for column in ("title", "ingredients", "instructions"):
            if column in data:
                fields.append(f"{column} = ?")
                values.append(data[column])

        if "is_public" in data:
            fields.append("is_public = ?")
            values.append(1 if data["is_public"] else 0)

        if not fields:
            return jsonify({"error": "nothing to update"}), 400

        db = get_db()

        row = db.execute(
            "SELECT owner_id FROM recipes WHERE id = ?",
            (recipe_id,),
        ).fetchone()

        if row is None:
            return jsonify({"error": "recipe not found"}), 404

        if row["owner_id"] != user_id and role != "admin":
            return jsonify({"error": "forbidden"}), 403

        values.append(recipe_id)

        try:
            db.execute(
                f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
                values,
            )
            db.commit()

        except sqlite3.IntegrityError:
            return jsonify({
                "error": "a recipe with that title already exists"
            }), 409

        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (recipe_id,),
        ).fetchone()

        return jsonify(recipe_to_dict(row)), 200

    # Recipe deletion
    @app.delete("/recipes/<int:recipe_id>")
    @token_required
    def delete_recipe(recipe_id):
        db = get_db()

        row = db.execute(
            "SELECT owner_id FROM recipes WHERE id = ?",
            (recipe_id,),
        ).fetchone()

        if row is None:
            return jsonify({"error": "recipe not found"}), 404

        user_id = g.current_user["id"]
        role = g.current_user["role"]

        if row["owner_id"] != user_id and role != "admin":
            return jsonify({"error": "forbidden"}), 403

        db.execute(
            "DELETE FROM recipes WHERE id = ?",
            (recipe_id,),
        )
        db.commit()

        return "", 204

    # User registration
    @app.post("/register")
    def register_user():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            data = {}

        username = data.get("username", "")
        email = data.get("email", "")
        password = data.get("password", "")

        if not all(
            isinstance(value, str) and value.strip()
            for value in (username, email, password)
        ):
            return jsonify({
                "error": "username, email, and password are required"
            }), 400

        username = username.strip()
        email = email.strip()
        password_hash = hash_password(password)

        db = get_db()

        try:
            cur = db.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash),
            )
            db.commit()

        except sqlite3.IntegrityError:
            return jsonify({
                "error": "username or email already in use"
            }), 409

        row = db.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()

        return jsonify({
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }), 201

    # User login
    @app.post("/login")
    def login():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            data = {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "error": "username and password required"
            }), 400

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if (
            not user
            or not isinstance(password, str)
            or not check_password_hash(user["password_hash"], password)
        ):
            return jsonify({
                "error": "Invalid username or password"
            }), 401

        secret = app.config.get("JWT_SECRET")

        if not secret:
            app.logger.error("JWT_SECRET is not configured")
            return jsonify({
                "error": "server configuration error"
            }), 500

        payload = {
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=2),
        }

        token = jwt.encode(
            payload,
            secret,
            algorithm="HS256",
        )

        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "token": token,
        }), 200

    return app
