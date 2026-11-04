#################################################################################
# SELF DOCUMENTING HELP                                                                       #
#################################################################################

.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = {{ cookiecutter.project_name }}
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

##@ Formatting
.PHONY: format
format: ## format code with ruff
	@uv run ruff format orion tests cli.py
	@uv run ruff check --select I --fix orion tests cli.py

##@ Linting
.PHONY: lint-ruff
lint-ruff: ## ruff (formatter, import sorter and linter)
	@uv run ruff format --check orion tests cli.py
	@uv run ruff check orion tests cli.py

.PHONY: lint-mypy
lint-mypy: ## mypy (static-type checker)
	@uv run mypy --config-file pyproject.toml orion

.PHONY: lint-mypy-report
lint-mypy-report: ## run mypy & create report
	@uv run mypy --config-file pyproject.toml orion --html-report ./mypy_html

lint: lint-ruff lint-mypy ## run all linters

.PHONY: mock
mock: ## make mocks for testing
	@uv run python tests/make_mock_data.py

.PHONY: test
test: ## run tests
	@uv run pytest -v --cov=orion --cov-report=term-missing

##@ Releases
.PHONY: bump-patch
bump-patch: ## bump version patch
	@uv run bump2version patch  --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: bump-minor
bump-minor: ## bump version minor
	@uv run bump2version minor  --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: bump-major
bump-major:  ## bump version major
	@uv run bump2version major  --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: release
release:  ## release package to pypi
	@uv build
	@uv publish
