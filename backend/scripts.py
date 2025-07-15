import asyncio
import os.path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils.timezone import now

from bot.api.speechkit import synthesize
from bot.text_templates.base import ru_months
from bot.text_templates.friday_gift import insight_phrases
from bot.text_templates.premium_space import (
    power_days_descriptions,
    universe_vip_advices,
)
from bot.utils.formatters import genderize
from core.choices import Genders


async def synthesize_static_text(base_dir: str, text: str, key: int | str):
    if not os.path.exists(base_dir):
        os.mkdir(os.path.join(base_dir))

    for g in Genders.values:
        file_content = await synthesize(genderize(text, gender=g))
        filename = f'{base_dir}/{key}_{g}.wav'
        with open(filename, 'wb') as f:
            f.write(file_content)
        print(f'Generated {filename}')


async def synthesize_power_days():
    month = ru_months[now().month]
    for number, text in power_days_descriptions.items():
        await synthesize_static_text(
            'assets/audio/power_days',
            text.replace('{month}', month),
            number,
        )


async def synthesize_universe_vip_advices():
    for symbol, text in universe_vip_advices.items():
        await synthesize_static_text(
            'assets/audio/universe_vip_advices',
            f'{symbol}.\n\n{text}',
            symbol,
        )


async def synthesize_insight_phrases():
    for i, insight in enumerate(insight_phrases):
        await synthesize_static_text(
            'assets/audio/insight_phrases',
            insight,
            i,
        )


async def synthesize_all():
    await synthesize_power_days()
    await synthesize_universe_vip_advices()
    await synthesize_insight_phrases()


if __name__ == '__main__':
    asyncio.run(synthesize_all())
