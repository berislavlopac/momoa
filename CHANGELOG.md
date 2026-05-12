# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.4.0] - 2026-05-12
### Added
- Pluggable engine architecture; `PydanticEngine` using Pydantic v2 and
  datamodel-code-generator, supporting JSON Schema drafts 4–2020-12
- `Serializable` runtime-checkable protocol in `momoa.engines`
- Python 3.13 and 3.14 added to test matrix
### Changed
- `Model` renamed to `StathamModel`, moved to `momoa.engines.statham`
- `UNDEFINED` sentinel moved from `momoa.model` to `momoa.engines.statham`
- Development tooling: replaced `pdm` with `uv`; raised Python floor to 3.11
### Removed
- `model_factory` parameter from `Schema` constructor (pass via
  `StathamEngine(model_factory=...)` instead)
- `momoa.model` module (use `momoa.engines.statham.UNDEFINED` and
  `momoa.engines.statham.StathamModel`)

## [0.3.0] - 2024-04-16
- Remove support for Python 3.8

## [0.2.3] - 2024-04-16
- Switch to token-based PyPI publishing

## [0.2.2] - 2024-04-16
- Fix documentation
- Update dependencies
- Clean up `pyproject.toml`
- Add Python 3.12 to CI

## [0.2.1] - 2023-04-20
- Add test for UUID format
- Update ruff configuration
- Add Python 3.11 to CI

## [0.2.0] - 2023-02-16
- Support custom model factory
- Dev environment: replaced `pylint` with `ruff`, `poetry` with `pdm`
- Improve tests using `mutmut`

## [0.1.2] - 2022-12-14
- Minor meta-improvements; no functional changes

## [0.1.1] - 2022-10-06
- Fix project metadata

## [0.1.0] - 2022-10-06
- Initial release
