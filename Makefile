build:
	@docker build -t drive-pictures-to-s3 .

format:
	@poetry run isort .
	@poetry run black .
	@poetry run ruff --fix .

install:
	@poetry install --with dev


lint:
	@poetry run ruff check .
	@poetry run black --check .
	@poetry run mypy . --exclude '/\.venv/'

lint/fix:
	@poetry run black .
	@poetry run ruff check --fix .

run:
	@poetry run python drive_pictures_to_s3/main.py

test:
	@poetry run pytest -n auto
