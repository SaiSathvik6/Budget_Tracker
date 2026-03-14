"""
Income source management for persistent custom income sources
"""
from database.connection import get_db
import config


class IncomeSourceModel:
    """Handle income source-related database operations"""
    
    @staticmethod
    def get_all_sources():
        """Get all income sources (default + custom)"""
        db = get_db()
        
        # Get custom sources from database
        custom_sources = db["income_sources"].find_one({"_id": "custom_income_sources"})
        
        if custom_sources and "sources" in custom_sources:
            # Merge default and custom sources
            all_sources = list(set(config.INCOME_SOURCES + custom_sources["sources"]))
            return sorted(all_sources)
        
        return config.INCOME_SOURCES
    
    @staticmethod
    def add_source(source_name):
        """Add a new custom income source"""
        db = get_db()
        
        try:
            # Get existing custom sources
            custom_sources = db["income_sources"].find_one({"_id": "custom_income_sources"})
            
            if custom_sources:
                # Add to existing list
                sources = custom_sources.get("sources", [])
                if source_name not in sources:
                    sources.append(source_name)
                    db["income_sources"].update_one(
                        {"_id": "custom_income_sources"},
                        {"$set": {"sources": sources}}
                    )
            else:
                # Create new document
                db["income_sources"].insert_one({
                    "_id": "custom_income_sources",
                    "sources": [source_name]
                })
            
            return True
        except Exception as e:
            print(f"Error adding income source: {e}")
            return False
    
    @staticmethod
    def remove_source(source_name):
        """Remove a custom income source"""
        db = get_db()
        
        try:
            # Only allow removing custom sources, not default ones
            if source_name in config.INCOME_SOURCES:
                return False
            
            custom_sources = db["income_sources"].find_one({"_id": "custom_income_sources"})
            
            if custom_sources and "sources" in custom_sources:
                sources = custom_sources["sources"]
                if source_name in sources:
                    sources.remove(source_name)
                    db["income_sources"].update_one(
                        {"_id": "custom_income_sources"},
                        {"$set": {"sources": sources}}
                    )
                    return True
            
            return False
        except Exception as e:
            print(f"Error removing income source: {e}")
            return False
