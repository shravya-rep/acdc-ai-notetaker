up:
	docker compose up --build

migrate:
	docker compose exec backend python manage.py migrate

shell:
	docker compose exec backend sh
