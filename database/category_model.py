"""
Category management for persistent custom categories
"""
from database.connection import get_db
import config


class CategoryModel:
    """Handle category-related database operations"""
    
    @staticmethod
    def get_all_categories():
        """Get all categories (default + custom)"""
        db = get_db()
        
        # Get custom categories from database
        custom_cats = db["categories"].find_one({"_id": "custom_categories"})
        
        if custom_cats and "categories" in custom_cats:
            # Merge default and custom categories
            all_categories = list(set(config.CATEGORIES + custom_cats["categories"]))
            return sorted(all_categories)
        
        return config.CATEGORIES
    
    @staticmethod
    def add_category(category_name):
        """Add a new custom category"""
        db = get_db()
        
        try:
            # Get existing custom categories
            custom_cats = db["categories"].find_one({"_id": "custom_categories"})
            
            if custom_cats:
                # Add to existing list
                categories = custom_cats.get("categories", [])
                if category_name not in categories:
                    categories.append(category_name)
                    db["categories"].update_one(
                        {"_id": "custom_categories"},
                        {"$set": {"categories": categories}}
                    )
            else:
                # Create new document
                db["categories"].insert_one({
                    "_id": "custom_categories",
                    "categories": [category_name]
                })
            
            return True
        except Exception as e:
            print(f"Error adding category: {e}")
            return False
    
    @staticmethod
    def remove_category(category_name):
        """Remove a custom category"""
        db = get_db()
        
        try:
            # Only allow removing custom categories, not default ones
            if category_name in config.CATEGORIES:
                return False
            
            custom_cats = db["categories"].find_one({"_id": "custom_categories"})
            
            if custom_cats and "categories" in custom_cats:
                categories = custom_cats["categories"]
                if category_name in categories:
                    categories.remove(category_name)
                    db["categories"].update_one(
                        {"_id": "custom_categories"},
                        {"$set": {"categories": categories}}
                    )
                    return True
            
            return False
        except Exception as e:
            print(f"Error removing category: {e}")
            return False
