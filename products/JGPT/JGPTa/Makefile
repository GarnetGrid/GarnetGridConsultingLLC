.PHONY: setup up down logs api web ingest-kb ingest-web

setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; fi
	@if [ ! -f jgpt-web/.env.local ]; then cp jgpt-web/.env.local.example jgpt-web/.env.local && echo "Created jgpt-web/.env.local"; fi

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

api-shell:
	docker exec -it jgpt_api /bin/bash

ingest-kb:
	docker exec -it jgpt_api python scripts/ingest_kb.py

ingest-web:
	docker exec -it jgpt_api python scripts/ingest_web.py
