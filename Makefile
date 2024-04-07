

main:
	@python3 app.py

run:
	@docker compose up --build --remove-orphans

run-production:
	@docker compose up -d --build --remove-orphans

logs:
	@docker compose logs -f --tail 100

down:
	@docker compose down --remove-orphans

build:
	@docker build -t api-ia-aws\:latest .

get-80-port-use:
	@sudo lsof -i :80

restart-production: build run-production

