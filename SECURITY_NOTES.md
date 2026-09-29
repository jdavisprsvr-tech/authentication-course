# Security baseline

- 2026-09-11:
  - Anonymous GET /recipes → 200, returns all recipes
  - Anonymous GET /recipes/1 → 200, returns recipe 1
  - Anonymous POST /recipes → 201, creates a new recipe (id 4)
  - Anonymous PATCH /recipes/4 → 200, updates that recipe
  - Anonymous DELETE /recipes/4 → 204, deletes that recipe

# Security Audit – Recipe API

2026-09-29:

## 1. Password storage

- `users.password_hash` stores PBKDF2-SHA256 hashes, not plaintext.
- Sample query:

  ```sql
  SELECT id, email, password_hash FROM users LIMIT 3;
  ```

  Example value:

  `pbkdf2:sha256:1000000$...$f98840f43b20e8...`

**Conclusion:** Passwords are safely stored as hashes.

---

## 2. Authentication (401 checks)

Test endpoint: `POST /recipes`

- Missing/empty token:

  ```bash
  curl -i -X POST http://localhost:5001/recipes \
    -H "Authorization: Bearer" \
    -H "Content-Type: application/json" \
    -d '{"title":"Pepper Pizza","ingredients":"pizza dough, cheese, peppers","instructions":"Add cheese and peppers to the dough and bake until golden."}'
  ```

  → `401 UNAUTHORIZED`, `{"error": "invalid authorization header"}`

- Expired token:

  → `401 UNAUTHORIZED`, `{"error": "token has expired, please log in again"}`

- Invalid/garbled token:

  → `401 UNAUTHORIZED`, `{"error": "invalid token"}`

**Conclusion:** Write routes require a valid, non-expired JWT.

---

## 3. Authorization (403, owner, admin)

Resource: `DELETE /recipes/5`, owned by Lexi (user id 5, role `user`).

- Bob (user, non-owner):

  ```bash
  DELETE /recipes/5 as Bob (role=user)
  ```

  → `403 FORBIDDEN`, `{"error": "forbidden"}`

- Lexi (owner, role=user):

  ```bash
  DELETE /recipes/5 as Lexi (role=user, owner)
  ```

  → `204 NO CONTENT`

- Allison (role=admin):

  ```bash
  DELETE /recipes/5 as Allison (role=admin)
  ```

  → `204 NO CONTENT`

**Conclusion:** Ownership and admin rules are enforced: non-owner users get `403`, owner and admin are allowed.

---

## 4. Old exploit regression test

Previous exploit:

- `POST /recipes` without any `Authorization` header used to create recipes.

Re-test:

```bash
curl -i -X POST http://localhost:5001/recipes \
  -H "Authorization: Bearer" \
  -H "Content-Type: application/json" \
  -d '{"title":"Pepper Pizza","ingredients":"pizza dough, cheese, peppers","instructions":"Add cheese and peppers to the dough and bake until golden."}'

  `401 UNAUTHORIZED, {"error": "invalid authorization header"}`

  conclusion the old unauthenticated-creation exploit is blocked and a valid token is required. 