# Endpoints That Must Never Be Cached

- `POST /login` — Returns an authentication token; credentials and tokens must be handled securely.
- `POST /register` — Creates a user account; this is a state-changing operation and must not be cached.
- `GET /recipes/<id>` — Must not be cached while recipe visibility and ownership protections are unresolved; private recipe data must not leak between users.
- `POST /recipes` — Creates a recipe; this is a state-changing operation and must not be cached.
- `PATCH /recipes/<id>` — Updates a recipe; this is a state-changing operation and must not be cached.
