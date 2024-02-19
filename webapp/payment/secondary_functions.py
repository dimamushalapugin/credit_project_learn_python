from datetime import datetime


def create_date_format(date_str: str) -> datetime.date:
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def floating_or_not(checkboxes):
    if checkboxes == 'floating':
        return True
    else:
        return False
