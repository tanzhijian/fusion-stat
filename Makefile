PATH := .

test:
	poetry run ruff ${PATH}
	poetry run mypy ${PATH}
	poetry run pytest ${PATH}
