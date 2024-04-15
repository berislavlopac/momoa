# Contribute to momoa

## Development Environment

[PDM](https://pdm.fming.dev) is used for dependency and package management. The steps for setting up the development environment:

1. Install PDM: either [globally](https://pdm.fming.dev/latest/#recommended-installation-method), or in a Python virtual environment (using `pip install pdm`).

2. Install the project (if outside a virtual environment, PDM will [create one](https://pdm.fming.dev/latest/usage/venv/#virtualenv-auto-creation)):

        $ pdm install -d


### Code Validation

[tox](https://tox.wiki) is being used to execute multiple code validation checks at once:

```shell
$ tox
```

This command will automatically run a number of code validation checks, as well as the unit test suite for multiple versions of Python.

**Note:** For local development, use `pyenv` to install multiple versions of Python and set them up as local in the root directory of the project; for example:

```shell
$ pyenv install 3.8.13
$ pyenv install 3.9.12
$ pyenv install 3.10.4
$ pyenv local 3.8.13 3.9.12 3.10.4
```

#### Manual Validation

There is a number of code quality checks that can be executed using PDM commands:

```shell
$ pdm run check-lint    # validates code linting using tools like ruff, black or isort
$ pdm run check-typing  # runs static type analysis using mypy
$ pdm run check-docs    # checks docstring content and structure
$ pdm run checks        # runs all of the above checks together
```

There is a separate command for running tests:

```shell
$ pdm run tests
```
Of course, tests can also be executed using `pytest` directly.


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
