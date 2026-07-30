.PHONY: install dev test lint format up down

install:
	pip install -r requirements.txt -r requirements-dev.txt

dev:
	uvicorn backend.app.main:app --reload

test:
	pytest --cov --cov-report=term-missing

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

up:
	docker compose up -d

down:
	docker compose down
