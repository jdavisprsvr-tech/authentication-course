import sqlite3

connection = sqlite3.connect("recipes.db")
connection.execute("ALTER TABLE recipes ADD COLUMN owner_id INTEGER")
connection.commit()
connection.close()

print("owner_id column added.")