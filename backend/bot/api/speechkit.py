import asyncio
import base64
import io

from pydub import AudioSegment

from bot.api.base import APIClient
from bot.loader import logger
from bot.settings import settings
from bot.text_utils import split_text


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
                'hints': [{'voice': 'jane'}, {'role': 'good'}],
            },
        ) as rsp:
            data = await rsp.json()
            logger.debug(data)
            if not data.get('result'):
                logger.info(data)
            result = data['result']

        logger.debug(f'Synthesized text ({result.get("lengthMs")} ms)')
        return base64.b64decode(result['audioChunk']['data'])

    async def synthesize_v1(self, text: str) -> bytes:
        logger.debug(f'Text length: {len(text)}')
        async with self.session.post(
            'speech/v1/tts:synthesize',
            data={
                'text': text[:4999],
                'voice': 'filipp',
                'emotion': 'friendly',
                'lang': 'ru-RU',
            },
        ) as rsp:
            data = await rsp.read()
            return data


async def synthesize(text: str) -> bytes:
    async with SpeechKit() as sk:
        audio_chunks = await asyncio.gather(
            *[sk.synthesize_v3(chunk) for chunk in split_text(text)],
        )
    audio = AudioSegment.empty()
    for chunk in audio_chunks:
        audio += AudioSegment.from_wav(
            io.BytesIO(chunk),
        )
    return audio.export(format='wav').read()
