from aiogram import F, Router, flags
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import get_weekly_quest_kb
from bot.keyboards.utils import keyboard_from_queryset
from core.models import Client, ClientWeeklyQuest, WeeklyQuest

router = Router()


@router.message(F.text == '🧩 Практики для роста')
@router.callback_query(F.data == 'to_weekly_quests_list')
async def weekly_quests_list(msg: Message | CallbackQuery):
    answer_func = msg.answer if isinstance(msg, Message) else msg.message.edit_text
    await answer_func(
        'Выбери, в каком челлендже ты хочешь участвовать',
        reply_markup=await keyboard_from_queryset(
            WeeklyQuest,
            'weekly_quest',
        ),
    )


@router.callback_query(F.data.startswith('weekly_quest'))
async def weekly_quest_detail(query: CallbackQuery):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await query.message.edit_text(
        quest.title,
        reply_markup=await get_weekly_quest_kb(quest),
    )


@router.callback_query(F.data.startswith('participate_in_weekly_quest'))
@flags.with_client
async def participate_in_weekly_quest(query: CallbackQuery, client: Client):
    quest = await WeeklyQuest.objects.aget(pk=query.data.split(':')[1])
    await ClientWeeklyQuest.objects.acreate(client=client, quest=quest)
    await query.message.edit_text(
        f'Теперь ты участвуешь в челлендже "{quest.title}"!\n'
        f'Я буду присылать тебе новое задание каждый день.',
    )
