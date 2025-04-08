import os

import django
from aiogram import F
from aiogram.enums import ChatType
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        commands,
        personal_account,
        personal_analysis,
        vip_services,
        invite_friend,
    )
    from bot.middlewares import WithClientMiddleware

    dp.include_routers(
        commands.router,
        personal_account.router,
        personal_analysis.router,
        vip_services.router,
        invite_friend.router,
    )
    dp.message.filter(F.chat.type == ChatType.PRIVATE)
    dp.message.middleware(WithClientMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [BotCommand(command='/start', description='Запустить бота')],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
