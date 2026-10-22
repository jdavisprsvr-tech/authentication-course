
"""Authentication routes for the Recipe Box API — BE104."""
from datetime import datetime, timedelta, timezone
import jwt
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256")


# User registration
@auth_bp.post("/register")
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

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "username or email already in use"
        }), 409

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }), 201


# User login
@auth_bp.post("/login")
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

    user = User.query.filter_by(username=username).first()

    if (
        user is None
        or not isinstance(password, str)
        or not check_password_hash(user.password_hash, password)
    ):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    secret = current_app.config.get("JWT_SECRET")

    if not secret:
        current_app.logger.error("JWT_SECRET is not configured")
        return jsonify({
            "error": "server configuration error"
        }), 500

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }

    token = jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )

    return jsonify({
        "id": user.id,
        "username": user.username,
        "token": token,
    }), 200
