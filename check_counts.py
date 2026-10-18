import sqlite3

for db_name, label in [
    ("recipes.db", "dev"),
    ("recipes_test.db", "test"),
]:
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    print(f"{label} users:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM recipes")
    print(f"{label} recipes:", cur.fetchone()[0])

    conn.close()
