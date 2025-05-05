import os

import django
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        compatability_energy,
        destiny_guide,
        friday_gift,
        invite_friend,
        load_media,
        menu,
        month_with_soul_muse,
        personal_account,
        personal_analysis,
        personal_day,
        premium_space,
        quests,
        registration,
        soul_muse_question,
        subscribe,
        universe_advice,
        vip_services,
    )
    from bot.middlewares import WithClientMiddleware

    dp.include_routers(
        registration.router,
        menu.router,
        subscribe.router,
        personal_analysis.router,
        compatability_energy.router,
        soul_muse_question.router,
        quests.router,
        universe_advice.router,
        personal_day.router,
        destiny_guide.router,
        friday_gift.router,
        month_with_soul_muse.router,
        premium_space.router,
        invite_friend.router,
        personal_account.router,
        vip_services.router,
        load_media.router,
    )
    dp.message.middleware(WithClientMiddleware())
    dp.callback_query.middleware(WithClientMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
            BotCommand(command='/menu', description='Главное меню'),
        ],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
