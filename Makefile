format:
	ruff format .

lint:
	ruff check .

fix:
	ruff check --fix .
	ruff format .

test:
	pytest

check:
	ruff format --check .
	ruff check .