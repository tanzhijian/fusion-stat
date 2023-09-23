test:
	poetry run ruff --format=github --target-version=py310 .
	poetry run mypy .
	poetry run pytest

init:
	poetry run python script/init.py
