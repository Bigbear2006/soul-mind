import os

import django
from aiogram import F
from aiogram.enums import ChatType
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import commands

    dp.include_routers(commands.router)
    dp.message.filter(F.chat.type == ChatType.PRIVATE)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [BotCommand(command='/start', description='Запустить бота')],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
