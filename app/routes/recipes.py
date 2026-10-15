
import sqlite3

from flask import Blueprint, g, jsonify, request

from app.auth import token_required
from app.db import get_db
from app.recipe_utils import recipe_to_dict


recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.get("/recipes")
def list_recipes():
    rows = get_db().execute(
        "SELECT * FROM recipes ORDER BY id"
    ).fetchall()

    return jsonify([
        recipe_to_dict(row) for row in rows
    ])


@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,),
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe_to_dict(row))


@recipes_bp.post("/recipes")
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
            (title, ingredients, instructions, is_public, author_id)
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


@recipes_bp.patch("/recipes/<int:recipe_id>")
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
        "SELECT author_id FROM recipes WHERE id = ?",
        (recipe_id,),
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    if row["author_id"] != user_id and role != "admin":
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


@recipes_bp.delete("/recipes/<int:recipe_id>")
@token_required
def delete_recipe(recipe_id):
    db = get_db()

    row = db.execute(
        "SELECT author_id FROM recipes WHERE id = ?",
        (recipe_id,),
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = g.current_user["id"]
    role = g.current_user["role"]

    if row["author_id"] != user_id and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    db.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,),
    )
    db.commit()

    return "", 204
