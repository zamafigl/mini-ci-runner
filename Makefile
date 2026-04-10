up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build -d

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

test:
	docker compose run --rm api pytest -v

test-runs:
	docker compose run --rm api pytest -v tests/test_runs.py

test-pipelines:
	docker compose run --rm api pytest -v tests/test_pipelines.py

migrate-up:
	docker compose run --rm api alembic upgrade head

migrate-current:
	docker compose run --rm api alembic current

migrate-create:
	docker compose run --rm api alembic revision --autogenerate -m "$(m)"

shell-api:
	docker compose exec api bash

shell-worker:
	docker compose exec worker sh
