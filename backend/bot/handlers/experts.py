from aiogram import Router

from bot.filters import IsExpert
from bot.handlers import answer_consult, consults_list

router = Router()
router.include_router(answer_consult.router)
router.include_router(consults_list.router)

router.message.filter(IsExpert())
router.callback_query.filter(IsExpert())
