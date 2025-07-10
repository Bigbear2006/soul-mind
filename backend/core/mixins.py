from django.utils.safestring import mark_safe

from bot.settings import settings


class AudioPlayerMixin:
    def audio_player(self, obj):
        url = (
            f'https://api.telegram.org/file/bot{settings.BOT_TOKEN}/'
            f'{obj.audio_file_path}'
        )
        return mark_safe(
            f'<audio controls src="{url}">'
            'Ваш браузер не поддерживает элемент audio.'
            '</audio>',
        )

    audio_player.short_description = 'Аудио'
