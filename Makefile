test:
	poetry run ruff .
	poetry run mypy .
	poetry run pytest

init:
	poetry run python script/init.py
