"""Extract the release notes for the current version from CHANGELOG.md.

Reads the version from pyproject.toml and prints the corresponding section
from CHANGELOG.md to stdout. Exits with a non-zero status if the section is
not found.

Usage: python scripts/extract_changelog.py [output-file]

If an output file path is given, the notes are written there; otherwise they
are printed to stdout.
"""

import re
import sys
import tomllib
from pathlib import Path


def main() -> None:
    root = Path(__file__).parent.parent

    with (root / "pyproject.toml").open("rb") as f:
        version = tomllib.load(f)["project"]["version"]

    text = (root / "CHANGELOG.md").read_text()

    pattern = r"(?sm)^## \[" + re.escape(version) + r"\][^\n]*\n(.*?)(?=^## \[|\Z)"
    match = re.search(pattern, text)
    if not match:
        print(f"No release notes found for {version}", file=sys.stderr)
        sys.exit(1)

    notes = match.group(1).strip() + "\n"

    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(notes)
    else:
        sys.stdout.write(notes)


if __name__ == "__main__":
    main()
