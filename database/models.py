"""
Database operations for budgets and expenses
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from bson import ObjectId
import config
from database.connection import get_db




class ExpenseModel:
    """Handle expense-related database operations"""
    
    @staticmethod
    def create_expense(date: datetime, category: str, description: str, amount: float) -> bool:
        """Create a new expense"""
        db = get_db()
        
        try:
            expense = {
                "date": date,
                "category": category,
                "description": description,
                "amount": amount,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            db[config.EXPENSES_COLLECTION].insert_one(expense)
            return True
        except Exception as e:
            print(f"Error creating expense: {e}")
            return False
    
    @staticmethod
    def get_expenses(start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None,
                     category: Optional[str] = None) -> List[Dict]:
        """Get expenses with optional filters"""
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
        
        expenses = list(db[config.EXPENSES_COLLECTION].find(query).sort("date", -1))
        return expenses
    
    @staticmethod
    def get_monthly_total(year: int, month: int) -> float:
        """Get total expenses for a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        return sum(exp["amount"] for exp in expenses)
    
    @staticmethod
    def get_current_month_total() -> float:
        """Get total expenses for current month"""
        now = datetime.now()
        return ExpenseModel.get_monthly_total(now.year, now.month)
    
    @staticmethod
    def get_category_breakdown(start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get expense breakdown by category"""
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        
        # Initialize with all known categories
        from database.category_model import CategoryModel
        all_categories = CategoryModel.get_all_categories()
        breakdown = {cat: 0.0 for cat in all_categories}
        
        # Add expenses, including any unknown categories
        for exp in expenses:
            category = exp["category"]
            if category in breakdown:
                breakdown[category] += exp["amount"]
            else:
                # Handle legacy/unknown categories
                breakdown[category] = breakdown.get(category, 0.0) + exp["amount"]
        
        return breakdown
    
    @staticmethod
    def get_daily_totals(start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get daily expense totals as DataFrame"""
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        
        if not expenses:
            return pd.DataFrame(columns=["date", "amount"])
        
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        daily = df.groupby("date")["amount"].sum().reset_index()
        
        return daily
    
    @staticmethod
    def update_expense(expense_id: str, date: datetime, category: str, 
                      description: str, amount: float) -> bool:
        """Update an existing expense"""
        db = get_db()
        
        try:
            result = db[config.EXPENSES_COLLECTION].update_one(
                {"_id": ObjectId(expense_id)},
                {
                    "$set": {
                        "date": date,
                        "category": category,
                        "description": description,
                        "amount": amount,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False
    
    @staticmethod
    def delete_expense(expense_id: str) -> bool:
        """Delete an expense"""
        db = get_db()
        
        try:
            result = db[config.EXPENSES_COLLECTION].delete_one({"_id": ObjectId(expense_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    @staticmethod
    def get_yearly_monthly_totals(year: int) -> Dict[int, float]:
        """Get monthly totals for a specific year"""
        totals = {}
        for month in range(1, 13):
            totals[month] = ExpenseModel.get_monthly_total(year, month)
        return totals
    
    @staticmethod
    def get_available_years() -> List[int]:
        """Get list of years that have expense data"""
        db = get_db()
        
        try:
            # Get all expenses and extract unique years
            expenses = db[config.EXPENSES_COLLECTION].find({}, {"date": 1})
            years = set()
            
            for exp in expenses:
                if "date" in exp and exp["date"]:
                    years.add(exp["date"].year)
            
            # Return sorted list (newest first)
            return sorted(list(years), reverse=True) if years else [datetime.now().year]
        except Exception as e:
            print(f"Error getting available years: {e}")
            return [datetime.now().year]
    
    @staticmethod
    def get_available_year_months() -> List[tuple]:
        """Get list of (year, month) tuples that have expense data"""
        db = get_db()
        
        try:
            # Get all expenses and extract unique year-month combinations
            expenses = db[config.EXPENSES_COLLECTION].find({}, {"date": 1})
            year_months = set()
            
            for exp in expenses:
                if "date" in exp and exp["date"]:
                    year_months.add((exp["date"].year, exp["date"].month))
            
            # Return sorted list (newest first)
            return sorted(list(year_months), reverse=True) if year_months else [(datetime.now().year, datetime.now().month)]
        except Exception as e:
            print(f"Error getting available year-months: {e}")
            return [(datetime.now().year, datetime.now().month)]
