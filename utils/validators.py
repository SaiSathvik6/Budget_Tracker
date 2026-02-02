"""
Input validation utilities
"""
from datetime import datetime
from typing import Tuple


def validate_amount(amount: float) -> Tuple[bool, str]:
    """
    Validate expense amount
    Returns: (is_valid, error_message)
    """
    if amount is None:
        return False, "Amount is required"
    
    if amount <= 0:
        return False, "Amount must be greater than 0"
    
    return True, ""


def validate_date(date: datetime) -> Tuple[bool, str]:
    """
    Validate expense date
    Returns: (is_valid, error_message)
    """
    if date is None:
        return False, "Date is required"
    
    if date > datetime.now():
        return False, "Date cannot be in the future"
    
    return True, ""


def validate_description(description: str) -> Tuple[bool, str]:
    """
    Validate expense description (optional)
    Returns: (is_valid, error_message)
    """
    # Description is now optional
    if description and len(description) > 200:
        return False, "Description is too long (max 200 characters)"
    
    return True, ""


def validate_category(category: str, valid_categories: list) -> Tuple[bool, str]:
    """
    Validate expense category
    Returns: (is_valid, error_message)
    """
    if not category:
        return False, "Category is required"
    
    if category not in valid_categories:
        return False, f"Invalid category. Must be one of: {', '.join(valid_categories)}"
    
    return True, ""
