import base64

from aiohttp import ClientSession

from bot.loader import logger
from bot.settings import settings


class SpeechKit:
    def __init__(self, **session_kwargs):
        self.session = ClientSession(
            'https://tts.api.cloud.yandex.net/tts/v3/',
            headers=self.headers,
            **session_kwargs,
        )

    @property
    def headers(self):
        return {'Authorization': f'Bearer {settings.YANDEX_API_KEY}'}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def synthesize(self, text: str) -> bytes:
        async with self.session.post(
            'utteranceSynthesis',
            json={
                'text': text,
                'hints': [{'voice': 'zhanar'}, {'role': 'friendly'}],
            },
        ) as rsp:
            data = await rsp.json()
            logger.info(data)
            result = data['result']

        logger.info(f'Synthesized text ({result.get("lengthMs")} ms)')
        return base64.b64decode(result['audioChunk']['data'])


async def synthesize(text: str) -> bytes:
    async with SpeechKit() as sk:
        audio = await sk.synthesize(text)
    return audio
