"""
MongoDB connection handler with singleton pattern
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import config
import streamlit as st


class DatabaseConnection:
    """Singleton class for MongoDB connection"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize MongoDB connection"""
        if self._client is None:
            try:
                self._client = MongoClient(
                    config.MONGO_URI,
                    serverSelectionTimeoutMS=5000
                )
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client[config.DATABASE_NAME]
                self._create_indexes()
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                st.error(f"Failed to connect to MongoDB: {e}")
                raise
    
    def _create_indexes(self):
        """Create necessary indexes for collections"""
        try:
            # Budget collection indexes
            budgets = self._db[config.BUDGETS_COLLECTION]
            budgets.create_index([("month", ASCENDING)], unique=True)
            
            # Expense collection indexes
            expenses = self._db[config.EXPENSES_COLLECTION]
            expenses.create_index([("date", DESCENDING)])
            expenses.create_index([("category", ASCENDING), ("date", DESCENDING)])
            
            # Income collection indexes
            income = self._db[config.INCOME_COLLECTION]
            income.create_index([("date", DESCENDING)])
            income.create_index([("source", ASCENDING), ("date", DESCENDING)])
            
        except Exception as e:
            st.warning(f"Index creation warning: {e}")
    
    def get_database(self):
        """Get database instance"""
        return self._db
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None


def get_db():
    """Helper function to get database instance"""
    conn = DatabaseConnection()
    return conn.get_database()
