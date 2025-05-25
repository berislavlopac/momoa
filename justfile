# List available recipes.
help:
    @just --list --unsorted

# Run unit tests and coverage.
test:
    uv run pytest --spec

# Run unit tests without additional options.
test-cov:
    uv run pytest --spec --cov

# Run linting and formating checks.
lint:
    uv run deptry .
    uv run ruff format --check .
    uv run ruff check .
    uv run pydocstyle momoa/

# Run static typing analysis.
type:
    uv run mypy --install-types --non-interactive

# Run security checks.
analyze:
    uvx vulture --min-confidence 100 momoa/
    uvx radon mi --show --multi --min B momoa/

# Run all checks.
check: lint analyze type

# Reformat the code using isort and ruff.
[confirm]
reformat:
    uv run ruff format .
    uv run ruff check --select I --fix .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    pdm export --prod --without-hashes

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate
