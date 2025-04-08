from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.reply import vip_services_kb

router = Router()


@router.message(F.text == 'VIP-Услуги')
async def vip_services_handler(msg: Message):
    await msg.answer('VIP-Услуги', reply_markup=vip_services_kb)
