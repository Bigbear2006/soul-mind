from datetime import datetime, UTC

from django.utils.timezone import now

from bot.text_templates.lunar_nodes import lunar_nodes


def get_lunar_nodes(date: datetime = None) -> dict[str, str] | None:
    if date is None:
        date = now()
    for date_range, nodes in lunar_nodes.items():
        start_date, end_date = date_range
        if start_date.replace(tzinfo=UTC) <= date <= end_date.replace(tzinfo=UTC):
            return nodes
    return None
