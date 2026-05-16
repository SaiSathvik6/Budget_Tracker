from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from bson import ObjectId
import config
from database.connection import get_db


class ExpenseModel:

    @staticmethod
    def create_expense(date: datetime, category: str, description: str, amount: float) -> bool:
        db = get_db()
        try:
            db[config.EXPENSES_COLLECTION].insert_one({
                "date": date,
                "category": category,
                "description": description,
                "amount": amount,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            })
            return True
        except Exception as e:
            print(f"Error creating expense: {e}")
            return False

    @staticmethod
    def get_expenses(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> List[Dict]:
        db = get_db()
        query = {}
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        if category:
            query["category"] = category
        return list(db[config.EXPENSES_COLLECTION].find(query).sort("date", -1))

    @staticmethod
    def get_monthly_total(year: int, month: int) -> float:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        return sum(e["amount"] for e in ExpenseModel.get_expenses(start_date, end_date))

    @staticmethod
    def get_category_breakdown(start_date: datetime, end_date: datetime) -> Dict[str, float]:
        from database.category_model import CategoryModel
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        breakdown = {cat: 0.0 for cat in CategoryModel.get_all_categories()}
        for exp in expenses:
            cat = exp["category"]
            breakdown[cat] = breakdown.get(cat, 0.0) + exp["amount"]
        return breakdown

    @staticmethod
    def get_daily_totals(start_date: datetime, end_date: datetime) -> pd.DataFrame:
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        if not expenses:
            return pd.DataFrame(columns=["date", "amount"])
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df.groupby("date")["amount"].sum().reset_index()

    @staticmethod
    def get_yearly_monthly_totals(year: int) -> Dict[int, float]:
        return {month: ExpenseModel.get_monthly_total(year, month) for month in range(1, 13)}

    @staticmethod
    def get_available_years() -> List[int]:
        db = get_db()
        try:
            expenses = db[config.EXPENSES_COLLECTION].find({}, {"date": 1})
            years = {e["date"].year for e in expenses if e.get("date")}
            return sorted(years, reverse=True) if years else [datetime.now().year]
        except Exception as e:
            print(f"Error getting available years: {e}")
            return [datetime.now().year]

    @staticmethod
    def get_available_year_months() -> List[tuple]:
        db = get_db()
        try:
            expenses = db[config.EXPENSES_COLLECTION].find({}, {"date": 1})
            ym = {(e["date"].year, e["date"].month) for e in expenses if e.get("date")}
            return sorted(ym, reverse=True) if ym else [(datetime.now().year, datetime.now().month)]
        except Exception as e:
            print(f"Error getting available year-months: {e}")
            return [(datetime.now().year, datetime.now().month)]

    @staticmethod
    def update_expense(expense_id: str, date: datetime, category: str, description: str, amount: float) -> bool:
        db = get_db()
        try:
            result = db[config.EXPENSES_COLLECTION].update_one(
                {"_id": ObjectId(expense_id)},
                {"$set": {
                    "date": date,
                    "category": category,
                    "description": description,
                    "amount": amount,
                    "updated_at": datetime.now(),
                }},
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False

    @staticmethod
    def delete_expense(expense_id: str) -> bool:
        db = get_db()
        try:
            result = db[config.EXPENSES_COLLECTION].delete_one({"_id": ObjectId(expense_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
