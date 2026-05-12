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
