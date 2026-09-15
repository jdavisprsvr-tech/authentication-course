from werkzeug.security import generate_password_hash, check_password_hash

password = "SuperSecret123!"

# 1. Generate a hash to store
password_hash = generate_password_hash(password, method="pbkdf2:sha256")
print("Stored hash:")
print(password_hash)
print()

# 2. Try verifying the correct password
is_correct = check_password_hash(password_hash, "SuperSecret123!")
print("Correct candidate result:", is_correct)

# 3. Try verifying the wrong password
is_wrong = check_password_hash(password_hash, "WrongPassword")
print("Wrong candidate result:", is_wrong)