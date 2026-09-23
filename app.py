"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""
import os
import sqlite3
import jwt
from flask import Flask, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, PyJWTError

load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET")

DATABASE = "recipes.db"

app = Flask(__name__)

app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET")

DATABASE = "recipes.db"




def hash_password(password: str) -> str:
    # use pbkdf2:sha256 explicitly to avoid scrypt issues
    return generate_password_hash(password, method="pbkdf2:sha256")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }


@app.get("/")
def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})


@app.get("/recipes")
def list_recipes():
    rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
    return jsonify([recipe_to_dict(r) for r in rows])


@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe_to_dict(row))


@app.post("/recipes")
def create_recipe():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "token is required"}), 401

    parts = auth_header.split(" ")

    if len(parts) != 2 or parts[0] != "Bearer":
        return jsonify({"error": "invalid authorization header"}),401

    token = parts[1]

    print("JWT_SECRET from config:", repr(app.config.get("JWT_SECRET")))

    try:
        payload = jwt.decode(
            token,
            app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )

        user_id = payload.get("sub")
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token has expired, please log in again"}), 401

    except jwt.PyJWTError as e:
        print("JWT ERROR:", repr(e))
        return jsonify({"error": "invalid token"}), 401
    
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
            return jsonify({"error": "title and ingredients are required"}), 400
    db = get_db()

    try:
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions, is_public)"
            " VALUES (?, ?, ?, ?)",
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(recipe_to_dict(row)), 201


@app.patch("/recipes/<int:recipe_id>")
def update_recipe(recipe_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "token is required"}), 401

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        return jsonify({"error": "invalid authorization"}), 401

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token has expired, please log in again"}), 401
    except jwt.PyJWTError:
        return jsonify({"error": "invalid token"}), 401
            
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(recipe_id)
    db = get_db()
    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    return jsonify(recipe_to_dict(row))


@app.delete("/recipes/<int:recipe_id>")
def delete_recipe(recipe_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "token is required"}), 401

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        return jsonify({"error": "invalid authorization header"}), 401

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except ExpiredSignatureError:
        return jsonify({"error": "token has expired, please log in again"}), 401
    except PyJWTError:
        return jsonify({"error": "invalid token"}), 401
    
    db = get_db()
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404
    return "", 204

@app.post("/register")
def register_user():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return {"error": "username, email, and password are required"}, 400

    password_hash = hash_password(password)

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # username or email already exists
        return jsonify({"error": "username or email already in use"}), 409

    row = db.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (cur.lastrowid,),
    ).fetchone()

    return jsonify(
        {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }
    ), 201

@app.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    db = get_db()

    if not username or not password:
        return {"error": "username and password required"}, 400

    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return {"error": "Invalid username or password"}, 401


    print("JWT_SECRET from config:", 
repr(app.config.get("JWT_SECRET")))

    # At this point, credentials are valid: issue a JWT
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(seconds=50),
    }


    token = jwt.encode(
        payload,
        app.config["JWT_SECRET"],
        algorithm="HS256",
    )

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "token": token,
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)

