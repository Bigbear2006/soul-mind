all: run

init:
	chmod +x ./backend/entrypoint.sh
	mkdir -p ./backend/logs
	cat .env.example > .env
	@echo "open and edit .env file"

run:
	docker-compose up --build -d

logs:
	docker-compose logs -f bot

restart:
	docker-compose restart bot

dump:
	docker-compose exec django python manage.py dumpdata \
	-o fixtures/quest_tags.json --indent 2 core.questtag

	docker-compose exec django python manage.py dumpdata -o fixtures/quests.json --indent 2 \
	core.dailyquest core.weeklyquest core.weeklyquesttask core.dailyquesttag core.weeklyquesttag

	docker-compose exec django python manage.py dumpdata \
	-o fixtures/topics.json --indent 2 core.topic

	docker-compose exec django python manage.py dumpdata \
	-o fixtures/expert_types.json --indent 2 core.experttype

load:
	docker-compose exec django python manage.py loaddata \
	fixtures/quest_tags.json fixtures/quests.json fixtures/topics.json fixtures/expert_types.json

admin:
	docker-compose exec django python manage.py createsuperuser