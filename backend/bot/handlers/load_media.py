import json

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    InputMediaDocument,
    Message,
)

from bot.settings import settings

router = Router()
router.message.filter(F.chat.id.in_(settings.ADMINS))


@router.message(F.text.lower() == 'load media')
async def load_media(msg: Message):
    sent_msg = await msg.answer_media_group(
        [
            InputMediaDocument(
                media=BufferedInputFile.from_file(
                    'assets/documents/privacy_policy.docx',
                ),
            ),
            InputMediaDocument(
                media=BufferedInputFile.from_file(
                    'assets/documents/public_offer.docx',
                ),
            ),
        ],
    )

    media = {
        'privacy_policy': sent_msg[0].document.file_id,
        'public_offer': sent_msg[1].document.file_id,
    }
    with open('media.json', 'w') as f:
        json.dump(media, f, indent=2)

    await msg.answer('Медиа загружены!')
