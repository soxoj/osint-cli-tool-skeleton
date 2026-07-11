PROJECT_NAME=osint_cli_tool_skeleton
LINT_FILES=$(PROJECT_NAME)

.PHONY: install install-dev install-all test rerun-tests lint format run serve mcp build clean rename

install:
	pip3 install .

install-dev:
	pip3 install -e '.[dev]'

install-all:
	pip3 install -e '.[all,dev]'

test:
	coverage run --source=./$(PROJECT_NAME) -m pytest tests
	coverage report -m
	coverage html

rerun-tests:
	pytest --lf -vv

lint:
	@echo 'syntax errors or undefined names'
	flake8 --count --select=E9,F63,F7,F82 --show-source --statistics $(LINT_FILES)
	@echo 'warning'
	flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=E731,W503,E501 $(LINT_FILES)
	@echo 'mypy'
	mypy $(LINT_FILES)

format:
	black $(LINT_FILES)

run:
	python3 -m $(PROJECT_NAME) --plugin string_info example

serve:
	python3 -m $(PROJECT_NAME) --server 0.0.0.0:8080

mcp:
	python3 -m $(PROJECT_NAME) --mcp

build:
	python3 -m build

clean:
	rm -rf reports htmlcov dist build *.egg-info .pytest_cache .coverage *.pdf

rename:
	python3 prepare.py
