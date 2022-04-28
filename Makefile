PROJECT_NAME=osint_cli_tool_skeleton
LINT_FILES=osint_cli_tool_skeleton

test:
	coverage run --source=./osint_cli_tool_skeleton -m pytest tests
	coverage report -m
	coverage html

rerun-tests:
	pytest --lf -vv

lint:
	@echo 'syntax errors or undefined names'
	flake8 --count --select=E9,F63,F7,F82 --show-source --statistics ${LINT_FILES}
	@echo 'warning'
	flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=E731,W503,E501 ${LINT_FILES}

	@echo 'mypy'
	mypy ${LINT_FILES}

format:
	@echo 'black'
	black --skip-string-normalization ${LINT_FILES}

clean:
	mv requirements.txt req.bak
	rm -rf reports htmcov dist build *.egg-info *.txt *.csv *.pdf
	mv req.bak requirements.txt

install:
	pip3 install .

rename:
	@python3 update.py