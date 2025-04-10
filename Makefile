all: run

init:
	chmod +x ./backend/entrypoint.sh
	mkdir -p ./backend/logs
	cat .env.example > .env
	@echo "open and edit .env file"

run:
	docker-compose up --build -d

dump:
	docker-compose exec django python manage.py dumpdata -o data.json --indent 2 \
	core.dailyquest core.weeklyquest core.weeklyquesttask

load:
	docker-compose exec django python manage.py loaddata data.json

createsuperuser:
	docker-compose exec django python manage.py createsuperuser