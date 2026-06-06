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

# Run tests across all supported Python versions via tox.
test-all:
    uv run tox

# Serve the documentation locally with live reload.
docs:
    # Silence the upstream `cgi` deprecation from json-ref-dict (see pyproject filterwarnings).
    PYTHONWARNINGS="ignore:'cgi' is deprecated:DeprecationWarning" uv run mkdocs serve --livereload

# Reformat the code using isort and ruff.
[confirm]
reformat:
    uv run ruff format .
    uv run ruff check --select I --fix .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    uv export --no-dev --no-hashes

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate

# Add a news fragment: `just news added` (auto id) or `just news fixed 42` (issue ref).
news type id=('+' + datetime('%s')):
    uv run towncrier create --edit {{id}}.{{type}}.md

# Preview the collated changelog for a version without writing it.
changelog-draft version:
    uv run towncrier build --draft --version {{version}}

# Suggest the next version from the pending news fragments (advisory).
suggest-version:
    uv run python scripts/suggest_version.py

# Validate, collate the changelog, commit, tag, and push a release (see CONTRIBUTE.md).
[confirm]
release version: check test
    @test -n "$(find release-notes -type f ! -name README.md)" || { echo "No news fragments in release-notes/ — use a direct tag for migration releases."; exit 1; }
    uv run towncrier build --yes --version {{version}}
    git add CHANGELOG.md release-notes
    git commit -m "Release {{version}}"
    git tag -a {{version}} -m "Release {{version}}"
    git push --follow-tags origin HEAD
