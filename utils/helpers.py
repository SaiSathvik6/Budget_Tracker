from datetime import datetime, timedelta
import config


def format_currency(amount: float) -> str:
    return f"{config.CURRENCY_SYMBOL}{amount:,.2f}"


def get_month_start_end(year: int, month: int) -> tuple:
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    return start_date, end_date


def get_current_month_range() -> tuple:
    now = datetime.now()
    return get_month_start_end(now.year, now.month)


def get_month_name(month: int) -> str:
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return months[month - 1]
