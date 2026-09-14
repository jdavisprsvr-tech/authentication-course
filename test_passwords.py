import sqlite3
from security import hash_password, verify_password


def main():
    # 1. Open your existing database
    conn = sqlite3.connect("recipes.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 2. Create a test user with a hashed password
    username = "testuser"
    email = "testuser@example.com"
    plain_password = "SuperSecret123!"

    # Delete any previous test user to avoid UNIQUE conflicts
    cur.execute("DELETE FROM users WHERE username = ?", (username,))

    password_hash = hash_password(plain_password)

    cur.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (username, email, password_hash),
    )
    conn.commit()

    print("Stored hash for testuser:")
    cur.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    print(dict(row))
    print()

    # 3. Verify correct and incorrect passwords
    stored_hash = row["password_hash"]

    print("Correct password check:",
          verify_password(stored_hash, "SuperSecret123!"))
    print("Wrong password check:",
          verify_password(stored_hash, "WrongPassword"))

    conn.close()


if __name__ == "__main__":
    main()