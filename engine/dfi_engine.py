from database.loader import load_food_interactions


class DFIEngine:
    def __init__(self):
        self.food_db = load_food_interactions()

    def find_interactions(self, drug_name: str):
        """
        Returns all food interactions for a given drug.
        """
        results = []

        if not drug_name:
            return results

        drug = drug_name.strip().lower()

        for item in self.food_db:

            if item["drug"].lower() == drug:
                results.append(item)

        return results
