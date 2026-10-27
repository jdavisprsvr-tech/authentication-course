
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, g, jsonify, request
from app.extensions import db, cache, limiter
from flask_limiter.util import get_remote_address
from app.models import Recipe
from app.auth_decorators import token_required
from app.recipe_utils import recipe_to_dict
from app.services.recipe_service import get_all_recipes
from app.services.recipe_service import (get_all_recipes, get_recipe_by_id, create_recipe_for_user, add_tags_to_recipe,)

def tag_rate_limit_key():
    if getattr(g, "current_user", None):
        return str(g.current_user["id"])
    return get_remote_address()

recipes_bp = Blueprint("recipes", __name__)

  # Public route
@recipes_bp.get("/")
def hello():
    return jsonify({
    "message": "Recipe Box API",
    "recipes": "/recipes",
})



@recipes_bp.get("/recipes")
@cache.cached(timeout=60, key_prefix=lambda: "recipes_list")
def list_recipes():
    recipes = get_all_recipes()
    return jsonify(recipes)


@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe)

@recipes_bp.get("/recipes/<int:recipe_id>/tags")
@token_required
def get_recipe_tags(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = int(g.current_user["id"])
    role = g.current_user["role"]

    if not recipe.is_public and recipe.owner_id != user_id and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    return jsonify({
        "recipe_id": recipe.id,
        "tags": sorted(tag.name for tag in recipe.tags),
    }), 200



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
    
    # target cached response for list_recipes not entire cache    
    cache.delete_cached(list_recipes)

    # status == "ok"
    return jsonify(payload), 201

@recipes_bp.post("/recipes/<int:recipe_id>/tags")
@token_required
@limiter.limit("10 per minute", key_func=tag_rate_limit_key)
def add_recipe_tags(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = int(g.current_user["id"])
    role = g.current_user["role"]

    if recipe.owner_id != user_id and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True)
    status, payload = add_tags_to_recipe(recipe_id, data)

    if status == "bad_request":
        return jsonify(payload), 400

    if status == "not_found":
        return jsonify(payload), 404

    if status == "conflict":
        return jsonify(payload), 409

    return jsonify(payload), 200




@recipes_bp.patch("/recipes/<int:recipe_id>")
@token_required
def update_recipe(recipe_id):
    user_id = g.current_user["id"]
    role = g.current_user["role"]
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "a JSON body is required"}), 400

    fields = ("title", "ingredients", "instructions")
    has_field = any(field in data for field in fields)

    if "is_public" in data:
        has_field = True

    if not has_field:
        return jsonify({"error": "nothing to update"}), 400

    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    if recipe.owner_id != user_id and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    for field in fields:
        if field in data:
            setattr(recipe, field, data[field])

    if "is_public" in data:
        recipe.is_public = 1 if data["is_public"] else 0

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    return jsonify(recipe_to_dict(recipe)), 200


@recipes_bp.delete("/recipes/<int:recipe_id>")
@token_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    user_id = int(g.current_user["id"])
    role = g.current_user["role"]

    if recipe.owner.id != user_id and role != "admin":
        return jsonify({"error": "forbidden"}), 403

    db.session.delete(recipe)
    db.session.commit()
    return "", 204





