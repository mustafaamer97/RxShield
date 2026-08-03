from database.loader import load_food_interactions


class DFIEngine:
    def __init__(self):
        self.food_db = load_food_interactions()

    def find_interactions(self, drug_name: str):
        if not drug_name:
            return []

        drug = drug_name.strip().lower()

        for item in self.food_db:
            if item["name"].strip().lower() == drug:
                return item

        return None
