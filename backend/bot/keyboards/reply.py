from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='🛠 Тех. поддержка')]],
    resize_keyboard=True,
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📌 Личностный разбор'),
            KeyboardButton(text='💞 Энергия вашей совместимости'),
        ],
        [
            KeyboardButton(text='👩🏽 Спроси у Soul Muse'),
            KeyboardButton(text='🧩 Практики для роста'),
        ],
        [
            KeyboardButton(text='🌟 Совет Вселенной'),
            KeyboardButton(text='📆 Твой личный день'),
        ],
        [
            KeyboardButton(text='🗺️ Путеводитель судьбы'),
            KeyboardButton(text='🎁 Пятничный подарок'),
        ],
        [
            KeyboardButton(text='📄 Месяц с Soul Muse'),
            KeyboardButton(text='💫 Премиум-пространство'),
        ],
        [
            KeyboardButton(text='🤝 Пригласить друга'),
            KeyboardButton(text='VIP-Услуги'),
        ],
        [
            KeyboardButton(text='👤 Личный кабинет'),
            KeyboardButton(text='🛠 Тех. поддержка'),
        ],
    ],
    resize_keyboard=True,
)
