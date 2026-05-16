import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "budget_tracker"
EXPENSES_COLLECTION = "expenses"

CURRENCY_SYMBOL = "₹"

CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Bills",
    "Other",
]

CHART_COLORS = {
    "Food": "#FF6B6B",
    "Transport": "#4ECDC4",
    "Rent": "#45B7D1",
    "Shopping": "#FFA07A",
    "Bills": "#98D8C8",
    "Other": "#C7CEEA",
}

PAGE_TITLE = "Budget Tracker"
PAGE_ICON = "💰"
LAYOUT = "wide"
