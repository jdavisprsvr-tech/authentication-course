# Security baseline

- 2026-09-11:
  - Anonymous GET /recipes → 200, returns all recipes
  - Anonymous GET /recipes/1 → 200, returns recipe 1
  - Anonymous POST /recipes → 201, creates a new recipe (id 4)
  - Anonymous PATCH /recipes/4 → 200, updates that recipe
  - Anonymous DELETE /recipes/4 → 204, deletes that recipe