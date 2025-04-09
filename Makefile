all: run

init:
	chmod +x ./backend/entrypoint.sh
	mkdir -p ./backend/logs
	cat .env.example > .env
	@echo "open and edit .env file"

run:
	docker-compose up --build -d