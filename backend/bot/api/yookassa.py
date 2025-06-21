import uuid

from aiohttp import BasicAuth

from bot.api.base import APIClient
from bot.loader import logger
from bot.schemas import Payment, PaymentStatus
from bot.settings import settings


class YookassaClient(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://api.yookassa.ru/v3/payments/',
            auth=self.auth,
            **session_kwargs,
        )

    @property
    def auth(self):
        return BasicAuth(
            settings.YOOKASSA_SHOP_ID,
            settings.YOOKASSA_SECRET_KEY,
        )

    @property
    def headers(self):
        return {'Idempotence-Key': str(uuid.uuid4())}

    async def create_payment(
        self,
        amount: int | float,
        description: str,
        email: str,
    ) -> Payment:
        async with self.session.post(
            '',
            headers=self.headers,
            json={
                'amount': {'value': amount, 'currency': settings.CURRENCY},
                'payment_method_data': {'type': 'bank_card'},
                'capture': True,
                'confirmation': {
                    'type': 'redirect',
                    'return_url': settings.BOT_LINK,
                },
                'description': description,
                'receipt': {
                    'customer': {'email': email},
                    'items': [
                        {
                            'amount': {
                                'value': amount,
                                'currency': settings.CURRENCY,
                            },
                            'description': description,
                            'vat_code': 1,
                            'quantity': 1,
                        },
                    ],
                },
            },
        ) as rsp:
            data = await rsp.json()

        if not data.get('confirmation'):
            logger.info(data)

        return Payment(
            id=data['id'],
            confirmation_url=data['confirmation']['confirmation_url'],
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        async with self.session.get(
            f'{payment_id}/',
            headers=self.headers,
        ) as rsp:
            data = await rsp.json()

        if not data.get('status'):
            logger.info(data)

        return PaymentStatus(data['status'])


async def create_payment(
    amount: float,
    description: str,
    email: str,
) -> Payment:
    async with YookassaClient() as yookassa:
        return await yookassa.create_payment(amount, description, email)


async def get_payment_status(payment_id: str) -> PaymentStatus:
    async with YookassaClient() as yookassa:
        return await yookassa.get_payment_status(payment_id)
