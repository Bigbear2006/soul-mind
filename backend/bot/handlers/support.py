from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == '🛠 Тех. поддержка')
async def support(msg: Message):
    await msg.answer(
        'Даже звёзды иногда сбиваются с курса.\n'
        'Если что-то не работает — просто скажи.\n'
        'Пиши в Telegram:\n'
        '@soulmind_support\n',
    )
