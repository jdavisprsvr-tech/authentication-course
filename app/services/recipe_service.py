from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.recipe_utils import recipe_to_dict
from app.models import Recipe




def get_all_recipes():
    recipes = Recipe.query.order_by(Recipe.id).all()
    return [recipe_to_dict(recipe) for recipe in recipes]


def get_recipe_by_id(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return None

    return recipe_to_dict(recipe)




def create_recipe_for_user(user_id, data):
    if not isinstance(data, dict) or not data:
        return ("bad_request", {"error": "a JSON body is required"})

    required = ("title", "ingredients", "instructions")

    for field in required:
        if field not in data:
            return ("bad_request", {"error": f"{field} is required"})

    is_public = 1 if data.get("is_public", False) else 0

    recipe = Recipe(
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data["instructions"],
        is_public=is_public,
        owner_id=user_id,
    )

    try:
        db.session.add(recipe)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return (
            "conflict",
            {"error": "a recipe with that title already exists"},
        )

    return ("ok", recipe_to_dict(recipe))
