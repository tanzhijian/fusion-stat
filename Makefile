open:
	subl fusion-stat.sublime-project

test:
	poetry run ruff --format=github --target-version=py310 .
	poetry run mypy .
	poetry run pytest
