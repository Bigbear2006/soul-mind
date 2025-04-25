from typing import Literal

from openai import AsyncOpenAI

from bot.templates.soul_muse_question import (
    get_answer_prompt,
    get_categorize_question_prompt,
)
from bot.templates.vip_services import get_vip_compatability_prompt


class SoulMuse:
    def __init__(self):
        self.client = AsyncOpenAI(base_url='https://api.proxyapi.ru/openai/v1')

    async def categorize_question(self, user_question: str) -> str:
        prompt = get_categorize_question_prompt(user_question)
        response = await self.client.responses.create(
            input=prompt,
            model='gpt-4.1',
        )
        return response.output_text

    async def answer(self, user_question: str) -> str:
        prompt = get_answer_prompt(user_question)
        response = await self.client.responses.create(
            input=prompt,
            model='gpt-4.1',
            max_output_tokens=270,
        )
        return response.output_text

    async def get_vip_compatability(
        self,
        connection_type: Literal['couple', 'family', 'friends', 'team'],
        persons: list[dict],
    ) -> str:
        prompt = get_vip_compatability_prompt(connection_type, persons)
        response = await self.client.responses.create(
            input=prompt,
            model='gpt-4.1',
        )
        return response.output_text
