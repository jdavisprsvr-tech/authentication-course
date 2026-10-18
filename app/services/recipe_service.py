import sqlite3
from app.db import get_db
from app.recipe_utils import recipe_to_dict



def get_all_recipes():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM recipes ORDER BY id"
    ).fetchall()

    return [recipe_to_dict(row) for row in rows]

def get_recipe_by_id(recipe_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if row is None:
        return None

    return recipe_to_dict(row)



def create_recipe_for_user(user_id, data):
    if not isinstance(data, dict) or not data:
        return ("bad_request", {"error": "a JSON body is required"})

    required = ("title", "ingredients", "instructions")

    for field in required:
        if field not in data:
            return ("bad_request", {"error": f"{field} is required"})

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
        return (
            "conflict",
            {"error": "a recipe with that title already exists"},
        )

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (cur.lastrowid,),
    ).fetchone()

    return ("ok", recipe_to_dict(row))