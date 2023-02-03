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
This is not needed for the CI, which runs one Python version (image) at a time.

#### Manual Validation

During development, each code check can be executed independently:

```shell
$ ruff .                                         # code linting
$ mypy --install-types --non-interactive momoa/  # Python typing analysis
$ black --check .                                # Python code formatting
$ isort --check .                                # Import statement optimisation
$ pydocstyle momoa/                              # styling and completeness of docstrings  
```

For unit tests use:

```shell
$ pytest --cov --spec
```

The indicated options add extra details to the report:

* `--cov` adds a test coverage report
* `--spec` formats the test report as a list of spec statements


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

The online documentation is built and hosted on ReadTheDocs, and configured in the `.readthedocs.yaml` file. The requirements file used for ReadTheDocs builds is located at `docs/requirements.txt`; to update it using PDM run the following command:

```shell
$ pdm export -o docs/requirements.txt -dG docs --without-hashes
```
