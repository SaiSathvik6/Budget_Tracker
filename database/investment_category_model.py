from database.connection import get_db
import config


class InvestmentCategoryModel:

    @staticmethod
    def get_all_categories():
        db = get_db()
        custom = db["investment_categories"].find_one({"_id": "custom_investment_categories"})
        if custom and "categories" in custom:
            all_cats = list(set(config.INVESTMENT_CATEGORIES + custom["categories"]))
            return sorted(all_cats)
        return list(config.INVESTMENT_CATEGORIES)

    @staticmethod
    def add_category(category_name: str) -> bool:
        db = get_db()
        try:
            doc = db["investment_categories"].find_one({"_id": "custom_investment_categories"})
            if doc:
                categories = doc.get("categories", [])
                if category_name not in categories:
                    categories.append(category_name)
                    db["investment_categories"].update_one(
                        {"_id": "custom_investment_categories"},
                        {"$set": {"categories": categories}},
                    )
            else:
                db["investment_categories"].insert_one({
                    "_id": "custom_investment_categories",
                    "categories": [category_name],
                })
            return True
        except Exception as e:
            print(f"Error adding investment category: {e}")
            return False

    @staticmethod
    def remove_category(category_name: str) -> bool:
        db = get_db()
        try:
            if category_name in config.INVESTMENT_CATEGORIES:
                return False
            doc = db["investment_categories"].find_one({"_id": "custom_investment_categories"})
            if doc and "categories" in doc:
                categories = doc["categories"]
                if category_name in categories:
                    categories.remove(category_name)
                    db["investment_categories"].update_one(
                        {"_id": "custom_investment_categories"},
                        {"$set": {"categories": categories}},
                    )
                    return True
            return False
        except Exception as e:
            print(f"Error removing investment category: {e}")
            return False
