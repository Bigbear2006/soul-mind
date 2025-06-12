from datetime import datetime

from bot.text_templates.lunar_nodes import lunar_nodes


def get_lunar_nodes(date: datetime = None) -> dict[str, str] | None:
    if date is None:
        date = datetime.now()
    for date_range, nodes in lunar_nodes.items():
        start_date, end_date = date_range
        if start_date <= date <= end_date:
            return nodes
    return None
