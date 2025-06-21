from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.api.yookassa import create_payment, get_payment_status
from bot.keyboards.inline.subscribe import pay_kb
from bot.schemas import PaymentStatus


async def send_payment_link(
    query: CallbackQuery,
    state: FSMContext,
    *,
    amount: int | float,
    description: str,
    email: str,
):
    payment = await create_payment(amount, description, email)
    await state.update_data(payment_id=payment.id)
    await query.message.edit_text(
        f'Ваша ссылка на оплату:\n\n{payment.confirmation_url}',
        reply_markup=pay_kb,
    )


async def check_payment(query: CallbackQuery, state: FSMContext):
    status = await get_payment_status(await state.get_value('payment_id'))
    if not status == PaymentStatus.SUCCEEDED:
        await query.answer(
            'К сожалению оплата не прошла. Попробуйте еще раз.',
            show_alert=True,
        )
        raise SkipHandler
