from openai import AsyncOpenAI

from bot.templates.soul_muse_question import (
    get_categorize_question_prompt,
    get_answer_prompt,
)


class SoulMuse:
    def __init__(self):
        self.client = client = AsyncOpenAI(
            base_url='https://api.proxyapi.ru/openai/v1'
        )

    async def categorize_question(self, user_question: str) -> str:
        prompt = get_categorize_question_prompt(user_question)
        response = await self.client.responses.create(
            input=prompt, model='gpt-4.1'
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
