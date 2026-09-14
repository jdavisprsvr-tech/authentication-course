from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
    """Return a one-way hash for storing in users.password_hash."""
    return generate_password_hash(plain_password, method="pbkdf2:sha256")


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Return True if the candidate password matches the stored hash."""
    return check_password_hash(stored_hash, candidate_password)