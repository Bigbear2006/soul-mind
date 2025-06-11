import json

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

from bot.settings import settings

router = Router()
router.message.filter(F.chat.id.in_(settings.ADMINS))


@router.message(F.text.lower() == 'load media')
async def load_media(msg: Message):
    documents_msg = await msg.answer_media_group(
        [
            InputMediaDocument(
                media=BufferedInputFile.from_file(
                    'assets/documents/privacy_policy.docx',
                    'Политика конфиденциальности SoulMind',
                ),
            ),
            InputMediaDocument(
                media=BufferedInputFile.from_file(
                    'assets/documents/public_offer.docx',
                    'Публичная оферта SoulMind',
                ),
            ),
        ],
    )

    images_msg = await msg.answer_media_group(
        [
            InputMediaPhoto(
                media=BufferedInputFile.from_file(
                    'assets/images/soul_mind.jpeg',
                ),
            ),
            InputMediaPhoto(
                media=BufferedInputFile.from_file(
                    'assets/images/soul_muse.png',
                ),
            ),
        ],
    )

    videos_msg = await msg.answer_media_group(
        [
            InputMediaVideo(
                media=BufferedInputFile.from_file(
                    'assets/videos/soul_mind.mov',
                ),
            ),
            InputMediaVideo(
                media=BufferedInputFile.from_file(
                    'assets/videos/soul_muse.mov',
                ),
            ),
        ],
    )

    media = {
        'privacy_policy': documents_msg[0].document.file_id,
        'public_offer': documents_msg[1].document.file_id,
        'soul_mind': images_msg[0].photo[-1].file_id,
        'soul_muse': images_msg[1].photo[-1].file_id,
        'soul_mind_video': videos_msg[0].video.file_id,
        'soul_muse_video': videos_msg[1].video.file_id,
    }
    with open('media.json', 'w') as f:
        json.dump(media, f, indent=2)

    await msg.answer('Медиа загружены!')
