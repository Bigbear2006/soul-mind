from core.models import Client


def get_daily_quest_text(client: Client, quest_text: str) -> str:
    return client.genderize(
        '🧩 Задание дня от Soul Muse\n'
        'Сегодня — маленький шаг к себе.\n'
        'Быстрый. Точный. Не ради галочки, а ради фокуса.\n\n'
        'Хочешь почувствовать, что день не просто начался, а начался по-твоему?\n'
        f'Вот задание:\n\n{quest_text}',
    )
