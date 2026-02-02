"""
Helper utility functions
"""
from datetime import datetime, timedelta
import config


def format_currency(amount: float) -> str:
    """Format amount as currency with Indian Rupee symbol"""
    return f"{config.CURRENCY_SYMBOL}{amount:,.2f}"


def format_date(date: datetime) -> str:
    """Format date as readable string"""
    return date.strftime("%d %b %Y")


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def get_month_start_end(year: int, month: int) -> tuple:
    """Get start and end datetime for a given month"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    return start_date, end_date


def get_current_month_range() -> tuple:
    """Get start and end datetime for current month"""
    now = datetime.now()
    return get_month_start_end(now.year, now.month)


def get_month_name(month: int) -> str:
    """Get month name from month number"""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month - 1]


def get_financial_year_range() -> tuple:
    """Get start and end datetime for current financial year (Apr-Mar)"""
    now = datetime.now()
    if now.month >= 4:
        start_date = datetime(now.year, 4, 1)
        end_date = datetime(now.year + 1, 3, 31, 23, 59, 59)
    else:
        start_date = datetime(now.year - 1, 4, 1)
        end_date = datetime(now.year, 3, 31, 23, 59, 59)
    
    return start_date, end_date
