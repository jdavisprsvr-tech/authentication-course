

from functools import wraps

import jwt
from jwt import ExpiredSignatureError, PyJWTError
from flask import current_app, g, jsonify, request

from app.models import User


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
        secret = current_app.config.get("JWT_SECRET")

        if not secret:
            current_app.logger.error("JWT_SECRET is not configured")
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

        user = User.query.with_entities(
            User.id,
            User.username,
            User.role,
        ).filter_by(id=user_id).first()

        if user is None:
            return jsonify({"error": "invalid token"}), 401

        g.current_user = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }

        return view_function(*args, **kwargs)

    return decorated
