.PHONY: up down test reindex logs

up: .env
	docker compose build
	docker compose run --rm app python -m app.search --rebuild
	docker compose up -d
	@echo "Open http://localhost:8000"

down:
	docker compose down

test: .env
	docker compose run --rm app pytest -q

reindex: .env
	docker compose run --rm app python -m app.search --rebuild

logs:
	docker compose logs -f app

.env:
	cp .env.example .env
