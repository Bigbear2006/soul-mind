from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📌 Личностный разбор'),
            KeyboardButton(text='💞 Энергия вашей совместимости'),
        ],
        [
            KeyboardButton(text='🤖 Спроси у SoulMind'),
            KeyboardButton(text='🧩 Практики для роста'),
        ],
        [
            KeyboardButton(text='🌟 Совет Вселенной'),
            KeyboardButton(text='📆 Твой личный день'),
        ],
        [
            KeyboardButton(text='🗺 Путеводитель судьбы'),
            KeyboardButton(text='🎁 Пятничный подарок'),
        ],
        [
            KeyboardButton(text='📄 Месяц с Soul Muse'),
            KeyboardButton(text='💫 Премиум-пространство'),
        ],
        [
            KeyboardButton(text='🤝 Пригласить друга'),
            KeyboardButton(text='👤 Личный кабинет'),
        ],
        [
            KeyboardButton(text='VIP-Услуги'),
        ],
    ],
    resize_keyboard=True,
)

vip_services_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мини-консультация с экспертом')],
        [KeyboardButton(text='Глубокий персональный отчёт')],
        [KeyboardButton(text='VIP-анализ совместимости')],
        [KeyboardButton(text='В меню')],
    ],
    resize_keyboard=True,
)
