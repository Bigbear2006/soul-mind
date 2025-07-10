from django.db import models


class SubscriptionPlans(models.TextChoices):
    TRIAL = 'trial', 'Тестовый период'  # only for filtering
    STANDARD = 'standard', '✨ SoulMind Стандарт'
    PREMIUM = 'premium', '💎 SoulMind Премиум'

    @staticmethod
    def subscription_plans_teaser():
        return (
            'Ты уже {gender:начал,начала} путь к себе.\n'
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
                '🧩 Ежедневные задания — +5 баллов за каждое\n\n'
                '🌀 Челленджи (7 дней) — 1 в месяц + бонусы за прохождение\n\n'
                '📆 Твой личный день — ежедневный прогноз на основе твоих данных\n\n'
                '🌟 Совет Вселенной — каждый день\n\n'
                '🗺️ Путеводитель судьбы — доступ ко всем астрособытиям и важным дням\n\n'
                '👩🏽 Soul Muse отвечает — 4 вопроса в месяц\n\n'
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
                '🧩 Ежедневные задания — +5 баллов за каждое\n\n'
                '🌀 Челленджи — без ограничений (баллы начисляются за 2 в месяц)\n\n'
                '📆 Твой личный день — ежедневный прогноз на основе твоих данных\n\n'
                '🌟 Совет Вселенной — каждый день\n\n'
                '🗺️ Путеводитель судьбы — доступ ко всем астрособытиям и важным дням\n\n'
                '👩🏽 Вопрос к Soul Muse — 15 вопросов + приоритетный ответ\n\n'
                '⚡ Доступ к новым фичам и челленджам — раньше всех\n\n'
                '🔮 VIP-совет от Soul Muse (персональный инсайт)\n\n'
                '✨ “Ответ Вселенной” — 1 раз в месяц\n\n'
                '🚀 “День силы” — твой главный день месяца\n\n'
                '🎁 Пятничный подарок от Soul Muse — каждую пятницу\n\n'
                '🎁 Бонусы при оформлении:\n\n'
                '🎁 Персональный прогноз на месяц\n\n'
                '🎁 “Твой главный ресурс” — послание месяца\n\n'
                '🎁 Твой сценарий месяца'
            )
        else:
            raise ValueError('Invalid subscription plan')


class Genders(models.TextChoices):
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class QuestStatuses(models.TextChoices):
    COMPLETED = 'completed', '⚡ {gender:Выполнил,Выполнила}!'
    SKIPPED = 'skipped', '⏭ Пропустить'


class Actions(models.TextChoices):
    COMPATABILITY_ENERGY = (
        'compatability_energy',
        'Энергия вашей совместимости',
    )
    SOUL_MUSE_QUESTION = 'soul_muse_question', 'Спроси у Soul Muse'
    WEEKLY_QUEST = 'weekly_quest', 'Участие в еженедельном квесте'

    UNIVERSE_ADVICE = 'universe_advice', 'Совет вселенной'
    PERSONAL_DAY = 'personal_day', 'Твой личный день'
    DESTINY_GUIDE = 'destiny_guide', 'Путеводитель судьбы'

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
    HD_ANALYST = 'hd_analyst', 'Эксперт Human Design'
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


class FridayGiftTypes(models.TextChoices):
    INSIGHT_PHRASES = 'insight_phrases', 'Инсайт'
    CARDS = 'cards', 'Карта Soul Muse'
    SYMBOLS = 'symbols', 'Интуитивный символ / образ недели'


class MiniConsultStatuses(models.TextChoices):
    WAITING = 'waiting', 'В ожидании'
    IN_PROGRESS = 'in_progress', 'В обработке'
    COMPLETED = 'completed', 'Завершена'


class PurchaseTypes(models.TextChoices):
    STANDARD_SUBSCRIPTION = 'standard_subscription', '✨ SoulMind Стандарт'
    PREMIUM_SUBSCRIPTION = 'premium_subscription', '💎 SoulMind Премиум'
    MINI_CONSULT = 'mini_consult', 'Мини-консультация с экспертом'
    VIP_PERSONAL_REPORT = 'vip_personal_report', 'Глубокий персональный отчет'
    VIP_COMPATABILITY = 'vip_compatability', 'VIP Совместимость'
    EXTRA_COMPATABILITY = 'extra_compatability', 'Дополнительные совместимости'
    EXTRA_SOUL_MUSE_QUESTION = (
        'extra_soul_muse_question',
        'Дополнительные вопросы к Soul Muse',
    )
