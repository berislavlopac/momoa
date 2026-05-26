# Contribute to momoa

## Development Environment

[uv](https://docs.astral.sh/uv/) is used for dependency and package management.
[just](https://just.systems/) provides the development task runner.

Install dependencies:

```shell
$ uv sync
```

### Code Validation

Run all checks (linting, static analysis, type checking):

```shell
$ just check
```

Individual checks:

```shell
$ just lint   # ruff format/check + pydocstyle
$ just type   # mypy static type analysis
$ just analyze  # vulture + radon
```

### Running Tests

```shell
$ just test
```

Tests can also be run directly with pytest:

```shell
$ uv run pytest
```

### Reformatting

```shell
$ just reformat
```

## Changelog

Changes are recorded as **news fragments** rather than by editing `CHANGELOG.md`
directly. Each change adds one file to `release-notes/`, named `<id>.<type>.md`,
containing a one-line description. `<type>` is the change category — `breaking`,
`added`, `changed`, `deprecated`, `removed`, `fixed`, `security` (see
`release-notes/README.md` for what each means and how it maps to a version bump).
`<id>` defaults to a unique timestamp (no reference); pass a PR/issue number to
render a `(#42)` reference instead.

```shell
$ just news added           # -> release-notes/+<timestamp>.added.md (no reference)
$ just news fixed 42        # -> release-notes/42.fixed.md (renders "(#42)")
```

Preview how the collated changelog will look for a given version, and get a
recommended version derived from the pending fragments:

```shell
$ just changelog-draft 0.5.0
$ just suggest-version       # e.g. "0.3.0 -> 0.4.0  (minor: added)"
```

`towncrier` folds the fragments into a dated `CHANGELOG.md` section at release time
(see below). The date is stamped automatically when the release is cut, so
fragments never carry a date — you don't need to know the release date in advance.

## Releasing

The release version lives in **exactly one place: the git tag**. `pyproject.toml`
declares the version as `dynamic` and `hatch-vcs` derives it from the tag at build
time, so there is no version number to bump by hand.

To cut a release, state the version once:

```shell
$ just release 0.5.0
```

This recipe:

1. Runs `just check` and `just test` first. If anything fails it aborts here, so a
   broken tree produces no changelog, commit, or tag.
2. Runs `towncrier build` to collate the news fragments into a new
   `## [0.5.0] - <today>` section in `CHANGELOG.md` and delete the fragments.
3. Commits the changelog, creates the `0.5.0` tag, and pushes the commit and tag.

Pushing the tag triggers the Semaphore pipeline, which runs the checks and the full
test matrix and — **only if they pass** — builds the package, publishes it to PyPI,
and creates the GitHub release (notes are extracted from the new changelog section).
Ordinary pushes without a tag only run the checks and tests; they never publish.
Prereleases (e.g. `0.5.0rc1`) are detected automatically and marked as such on GitHub.

> Because the tag is created locally before CI runs, a CI failure leaves a tag that
> published nothing. To redo the release, delete the tag and try again:
>
> ```shell
> $ git push --delete origin 0.5.0 && git tag -d 0.5.0
> ```

## API Documentation

The project documentation can be served locally by running:

```shell
$ mkdocs serve
```

To build the static documentation site, run:

```shell
$ mkdocs build
```

This will create the HTML documentation in the `site` directory.

The online documentation is built and hosted on ReadTheDocs, and configured in the `.readthedocs.yaml` file.
