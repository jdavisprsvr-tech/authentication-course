
import sqlite3

from flask import Blueprint, g, jsonify, request

from app.auth import token_required
from app.db import get_db
from app.recipe_utils import recipe_to_dict
from app.services.recipe_service import get_all_recipes
from app.services.recipe_service import get_recipe_by_id
from app.services.recipe_service import (get_all_recipes, get_recipe_by_id, create_recipe_for_user,)


recipes_bp = Blueprint("recipes", __name__)

  # Public route
@recipes_bp.get("/")
def hello():
    return jsonify({
    "message": "Recipe Box API",
    "recipes": "/recipes",
})



@recipes_bp.get("/recipes")
def list_recipes():
    recipes = get_all_recipes()
    return jsonify(recipes)


@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe)



@recipes_bp.post("/recipes")
@token_required
def create_recipe():
    user_id = g.current_user["id"]
    data = request.get_json(silent=True)

    status, payload = create_recipe_for_user(user_id, data)

    if status == "bad_request":
        return jsonify(payload), 400
    if status == "conflict":
        return jsonify(payload), 409

    # status == "ok"
    return jsonify(payload), 201



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
