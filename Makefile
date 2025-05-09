.PHONY: help
.PHONY: default
default: install


install:
	uv sync --all-extras --all-groups --frozen
	uv tool install pre-commit --with pre-commit-uv --force-reinstall
	uv run pre-commit install

install-docs:
	uv sync --group docs --frozen --no-group dev

update:
	uv lock
	uvx pre-commit autoupdate
	$(MAKE) install

test:
	uv run pytest

check:
	uv run pre-commit run --all-files

coverage:
	uv run pytest --cov=py_code_mcp_server --cov-report=xml

cov:
	uv run pytest --cov=py_code --cov-report=term-missing

mypy:
	uv tool run mypy py_code --config-file pyproject.toml

# Add doctests target to specifically run doctest validation
doctest: install-docs doc install

# Update doc target to run doctests as part of documentation build
doc:
	uv run --no-project sphinx-build -M doctest docs/source docs/build/ -W --keep-going --fresh-env
	uv run --no-project sphinx-build -M html docs/source docs/build/ -W --keep-going --fresh-env



check-all: check test mypy doc


run:
	uv run --with fastmcp fastmcp dev run_fastmcp.py:fastmcp

run-dev:
	uv run python -m uvicorn "py_code.integrated_server:create_combined_server" --reload --host 127.0.0.1 --port 9090

# Alternative run option with watching capability but using the standard server startup
run-watch:
	uv run watchfiles "python -m py_code.mcp_server.__main__ --host 127.0.0.1 --port 9090" py_code
