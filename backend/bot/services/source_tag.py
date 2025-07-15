from core.models import Client, SourceTag


async def set_source_tag(client: Client, tag: str | None) -> bool:
    if not tag:
        return False

    if tag.startswith('sl-'):
        tag = 'yandex'

    try:
        tag = await SourceTag.objects.aget(pk=tag)
    except SourceTag.DoesNotExist:
        return False

    client.source_tag = tag
    await client.asave()
    return True
