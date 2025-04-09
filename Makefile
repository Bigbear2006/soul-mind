all: run

init:
	mkdir -p ./backend/logs
	cat env.example > .env
	@echo "open and edit .env file"

run:
	docker-compose up --build -d