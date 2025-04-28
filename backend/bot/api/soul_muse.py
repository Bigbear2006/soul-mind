from openai import NOT_GIVEN, AsyncOpenAI


class SoulMuse:
    def __init__(self):
        self.client = AsyncOpenAI(base_url='https://api.proxyapi.ru/openai/v1')

    async def answer(
        self,
        prompt: str,
        *,
        max_output_tokens: int = NOT_GIVEN,
    ) -> str:
        response = await self.client.responses.create(
            input=prompt,
            model='gpt-4.1',
            max_output_tokens=max_output_tokens,
        )
        return response.output_text
