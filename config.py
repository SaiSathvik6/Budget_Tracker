"""
Configuration settings for Budget Tracking Application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "budget_tracker"
EXPENSES_COLLECTION = "expenses"
INCOME_COLLECTION = "income"

# Application Settings
CURRENCY_SYMBOL = "₹"

# Expense Categories
CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Bills",
    "Other"
]

# Income Sources
INCOME_SOURCES = [
    "Salary",
    "Freelance",
    "Investment",
    "Gift",
    "Refund",
    "Other"
]

# Chart Colors
CHART_COLORS = {
    "Food": "#FF6B6B",
    "Transport": "#4ECDC4",
    "Rent": "#45B7D1",
    "Shopping": "#FFA07A",
    "Bills": "#98D8C8",
    "Other": "#C7CEEA"
}

# Income Source Colors
INCOME_COLORS = {
    "Salary": "#4CAF50",
    "Freelance": "#2196F3",
    "Investment": "#9C27B0",
    "Gift": "#FF9800",
    "Refund": "#00BCD4",
    "Other": "#607D8B"
}

# Page Configuration
PAGE_TITLE = "Budget Tracker"
PAGE_ICON = "💰"
LAYOUT = "wide"
