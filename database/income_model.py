"""
Income model for tracking money inflow
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from bson import ObjectId
import config
from database.connection import get_db


class IncomeModel:
    """Handle income-related database operations"""
    
    @staticmethod
    def create_income(date: datetime, source: str, description: str, amount: float) -> bool:
        """Create a new income entry"""
        db = get_db()
        
        try:
            income = {
                "date": date,
                "source": source,
                "description": description,
                "amount": amount,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            db[config.INCOME_COLLECTION].insert_one(income)
            return True
        except Exception as e:
            print(f"Error creating income: {e}")
            return False

    @staticmethod
    def get_total_income(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """Get total income within a period"""
        incomes = IncomeModel.get_incomes(start_date, end_date)
        return sum(inc["amount"] for inc in incomes)
    
    @staticmethod
    def get_incomes(start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None,
                    source: Optional[str] = None) -> List[Dict]:
        """Get incomes with optional filters"""
        db = get_db()
        query = {}
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        
        if source:
            query["source"] = source
        
        incomes = list(db[config.INCOME_COLLECTION].find(query).sort("date", -1))
        return incomes
    
    @staticmethod
    def get_monthly_total(year: int, month: int) -> float:
        """Get total income for a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        incomes = IncomeModel.get_incomes(start_date, end_date)
        return sum(inc["amount"] for inc in incomes)
    
    @staticmethod
    def get_current_month_total() -> float:
        """Get total income for current month"""
        now = datetime.now()
        return IncomeModel.get_monthly_total(now.year, now.month)
    
    @staticmethod
    def get_source_breakdown(start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get income breakdown by source"""
        incomes = IncomeModel.get_incomes(start_date, end_date)
        
        breakdown = {}
        for inc in incomes:
            source = inc["source"]
            breakdown[source] = breakdown.get(source, 0.0) + inc["amount"]
        
        return breakdown
    
    @staticmethod
    def get_daily_totals(start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get daily income totals as DataFrame"""
        incomes = IncomeModel.get_incomes(start_date, end_date)
        
        if not incomes:
            return pd.DataFrame(columns=["date", "amount"])
        
        df = pd.DataFrame(incomes)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        daily = df.groupby("date")["amount"].sum().reset_index()
        
        return daily
    
    @staticmethod
    def update_income(income_id: str, date: datetime, source: str, 
                     description: str, amount: float) -> bool:
        """Update an existing income entry"""
        db = get_db()
        
        try:
            result = db[config.INCOME_COLLECTION].update_one(
                {"_id": ObjectId(income_id)},
                {
                    "$set": {
                        "date": date,
                        "source": source,
                        "description": description,
                        "amount": amount,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating income: {e}")
            return False
    
    @staticmethod
    def delete_income(income_id: str) -> bool:
        """Delete an income entry"""
        db = get_db()
        
        try:
            result = db[config.INCOME_COLLECTION].delete_one({"_id": ObjectId(income_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting income: {e}")
            return False
    
    @staticmethod
    def get_yearly_monthly_totals(year: int) -> Dict[int, float]:
        """Get monthly income totals for a specific year"""
        totals = {}
        for month in range(1, 13):
            totals[month] = IncomeModel.get_monthly_total(year, month)
        return totals
