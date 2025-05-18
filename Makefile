.PHONY: help
.PHONY: default
default: install


install:
	uv sync --all-extras --all-groups --frozen
	uvx pre-commit install

install-docs:
	uv sync --group docs --frozen --no-group dev

update:
	uv lock -n
	uvx pre-commit autoupdate
	$(MAKE) install

test: install
	uv run pytest

check: install
	uvx  pre-commit run --all-files

coverage: install
	uv run pytest --cov=dev_kit_mcp_server --cov-report=xml

cov: install
	uv run pytest --cov=dev_kit_mcp_server --cov-report=term-missing

mypy: install
	uv run mypy dev_kit_mcp_server --config-file pyproject.toml

doctest: install-docs doc

doc:
	uv run --no-sync sphinx-build -M doctest docs/source docs/build/ -W --keep-going --fresh-env
	uv run --no-sync sphinx-build -M html docs/source docs/build/ -W --keep-going --fresh-env

check-all: check test mypy doc

run:
	uvx --from pyproject.toml dev-kit-mcp-server

dev:
	npx @modelcontextprotocol/inspector@latest node build/index.js
