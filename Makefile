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
	uv run pytest --cov=my_pkg --cov-report=xml # todo: change my_pkg to the actual package name

cov:
	uv run pytest --cov=my_pkg --cov-report=term-missing # todo: change my_pkg to the actual package name

mypy:
	uv tool run mypy my_pkg --config-file pyproject.toml
# todo: chanege my_pkg to the actual package name

doc:
	uv run sphinx-build -M html docs/source docs/build/


doctest:
	uv run sphinx-build -M doctest docs/source docs/build/ -W --keep-going

# Optional target that builds docs but ignores warnings
doc-build:
	uv run sphinx-build -M html docs/source docs/build/


doc: doctest doc-build

check-all: check test mypy doc
