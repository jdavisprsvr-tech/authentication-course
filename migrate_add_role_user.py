import sqlite3

connection = sqlite3.connect("recipes.db")
connection.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user';")
connection.commit()
connection.close()

print("role column added.")