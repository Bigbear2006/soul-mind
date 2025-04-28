from django.db import models


class SubscriptionPlans(models.TextChoices):
    STANDARD = 'standard', '✨ SoulMind Стандарт'
    PREMIUM = 'premium', '💎 SoulMind Премиум'

    @staticmethod
    def subscription_plans_teaser():
        return (
            'Ты уже начал(а) путь к себе.\n'
            'Теперь просто выбери, как глубоко ты хочешь идти.\n\n'
            '✨ SoulMind Стандарт.\n'
            'Идти вглубь. Спокойно. В своём ритме.\n\n'
            '💎 SoulMind Премиум\n'
            'Без ограничений. Глубже. Ближе к себе.'
        )

    @property
    def price(self):
        if self == SubscriptionPlans.STANDARD:
            return 500
        elif self == SubscriptionPlans.PREMIUM:
            return 1200
        else:
            raise ValueError('Invalid subscription plan')

    @property
    def teaser(self):
        if self == SubscriptionPlans.STANDARD:
            return (
                '✨ Тариф «Стандарт» (500 ₽ / мес)\n\n'
                'Для тех, кто хочет идти вглубь — в своём ритме.\n'
                'Ты получаешь доступ ко всему основному функционалу:\n\n'
                '📌 Полный разбор личности — развернутая карта твоей сути\n\n'
                '🔮 Совместимость — 3 расчёта в месяц\n\n'
                '🧩 Ежедневные задания — +5 баллов за действие, до 155 в месяц\n\n'
                '🌀 Челленджи (7 дней) — 1 в месяц + бонусы за прохождение\n\n'
                '📆 Твой личный день — ежедневный прогноз на основе твоих данных\n\n'
                '🌟 Совет Вселенной — каждый день\n\n'
                '🗺️ Путеводитель судьбы — доступ ко всем астрособытиям и важным дням\n\n'
                '🤖 Soul Muse отвечает — 4 вопроса в месяц + возможность докупить\n\n'
                '🎁 Бонусы при оформлении:\n\n'
                '🎁 Персональный прогноз на месяц\n\n'
                '🎁 “Твой главный ресурс” — послание месяца\n\n'
                '🎁 Пятничный подарок от Soul Muse — каждую пятницу'
            )
        elif self == SubscriptionPlans.PREMIUM:
            return (
                '💎 Тариф «Премиум» (1200 ₽ / мес)\n\n'
                'Для тех, кто готов жить глубже.\n'
                'Ты в пространстве, где нет ограничений — и есть особое внимание.\n\n'
                '📌 Полный разбор личности\n\n'
                '🔮 Совместимость — безлимит\n\n'
                '🧩 Ежедневные задания — +5 баллов за действие, до 155 в месяц\n\n'
                '🌀 Челленджи — без ограничений (баллы начисляются за 2 в месяц)\n\n'
                '📆 Твой личный день — ежедневный прогноз на основе твоих данных\n\n'
                '🌟 Совет Вселенной — каждый день\n\n'
                '🗺️ Путеводитель судьбы — доступ ко всем астрособытиям и важным дням\n\n'
                '🤖 Вопрос к Soul Muse — 15 вопросов + приоритетный ответ\n\n'
                '⚡ Доступ к новым фичам и челленджам — раньше всех\n\n'
                '🎁 Бонусы при оформлении:\n\n'
                '🎁 Персональный прогноз на месяц\n\n'
                '🎁 “Твой главный ресурс” — послание месяца\n\n'
                '🎲 “Код удачи 2025” — годовой прогноз\n\n'
                '🔮 VIP-совет от Soul Muse (персональный инсайт)\n\n'
                '✨ “Ответ Вселенной” — 1 раз в месяц\n\n'
                '🚀 “День силы” — твой главный день месяца\n\n'
                '🎁 Пятничный подарок от Soul Muse — каждую пятницу'
            )
        else:
            raise ValueError('Invalid subscription plan')


class Genders(models.TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class QuestStatuses(models.TextChoices):
    COMPLETED = 'completed', '⚡ Выполнил(а)!'
    SKIPPED = 'skipped', '⏭ Пропустить'


class Actions(models.TextChoices):
    COMPATABILITY_ENERGY = (
        'compatability_energy',
        'Энергия вашей совместимости',
    )
    SOUL_MUSE_QUESTION = 'soul_muse_question', 'Спроси у Soul Muse'
    FRIDAY_GIFT = 'friday_gift', 'Пятничный подарок'
    POWER_DAY = 'power_day', 'Твой День силы'
    UNIVERSE_ANSWER = 'universe_answer', 'Ответ Вселенной'
    SOUL_MUSE_VIP_ANSWER = 'soul_muse_vip_answer', 'VIP-совет от Soul Muse'


class MonthTextTypes(models.TextChoices):
    MONTH_FORECAST = 'month_forecast', 'Персональный прогноз на месяц'
    MONTH_MAIN_RESOURCE = 'month_main_resource', 'Главный ресурс месяца'
    MONTH_SCRIPT = 'month_script', 'Твой сценарий месяца'


class ExpertTypes(models.TextChoices):
    ASTROLOGIST = 'astrologist', 'Астролог'
    NUMEROLOGIST = 'numerologist', 'Нумеролог'
    PSYCHOLOGIST = 'psychologist', 'Психолог'
    HD_ANALYST = 'hd_analyst', 'Аналитик Human Design'
    SPIRITUAL_MENTOR = 'spiritual_mentor', 'Духовный наставник-энергопрактик'


class Intentions(models.TextChoices):
    FIND_INNER_ANSWERS = 'find_inner_answers', 'Найти внутренние ответы'
    SOLVE_CERTAIN_PROBLEM = (
        'solve_certain_problem',
        'Решить конкретную проблему',
    )
    CURIOSITY = 'curiosity', 'Любопытство'


class ExperienceTypes(models.TextChoices):
    FIRST_TIME = 'first_time', 'Впервые'
    SOME_EXPERIENCE = 'some_experience', 'У меня есть небольшой опыт'
    PRO = 'pro', 'Я практик или профи'


class FeelingsTypes(models.TextChoices):
    IN_RESOURCE = 'in_resource', 'В ресурсе'
    IN_SEARCH = 'in_search', 'В поиске'
    AT_BOTTOM = 'at_bottom', 'У дна (но чувствую движение)'


class MiniConsultFeedbackRatings(models.TextChoices):
    GOOD = 'good', 'В точку'
    NOT_BAD = 'not_bad', 'Неплохо, но можно глубже'
    BAD = 'bad', 'Не отозвалось'
