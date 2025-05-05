import base64

from bot.api.base import APIClient
from bot.loader import logger
from bot.settings import settings


class SpeechKit(APIClient):
    def __init__(self, **session_kwargs):
        super().__init__(
            'https://tts.api.cloud.yandex.net/',
            headers=self.headers,
            **session_kwargs,
        )

    @property
    def headers(self):
        return {'Authorization': f'Api-Key {settings.YANDEX_API_KEY}'}

    async def synthesize_v3(self, text: str) -> bytes:
        async with self.session.post(
            'tts/v3/utteranceSynthesis',
            json={
                'text': text,
                'hints': [{'voice': 'zhanar'}, {'role': 'friendly'}],
            },
        ) as rsp:
            data = await rsp.json()
            logger.debug(data)
            result = data['result']

        logger.info(f'Synthesized text ({result.get("lengthMs")} ms)')
        return base64.b64decode(result['audioChunk']['data'])

    async def synthesize_v1(self, text: str) -> bytes:
        logger.info(f'Text length: {len(text)}')
        async with self.session.post(
            'speech/v1/tts:synthesize',
            data={
                'text': text[:5000],
                'voice': 'filipp',
                'emotion': 'friendly',
                'lang': 'ru-RU',
            },
        ) as rsp:
            data = await rsp.read()
            return data


async def synthesize(text: str) -> bytes:
    async with SpeechKit() as sk:
        audio = await sk.synthesize_v1(text)
    return audio
