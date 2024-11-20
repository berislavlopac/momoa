# List available recipes.
help:
    @just --list --unsorted

# Run unit tests and coverage.
tests:
    pytest --spec --cov

# Run unit tests without additional options.
tests-quick:
    pytest

# Run linting and formating checks.
check-lint:
    ruff format --check .
    isort --check .
    ruff check .
    deptry .

# Run static typing analysis.
check-typing:
    mypy --install-types --non-interactive

# Run all checks.
checks: check-lint check-typing

# Reformat the code using isort and ruff.
[confirm]
reformat:
    isort .
    ruff format .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    pdm export --prod --without-hashes

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate
