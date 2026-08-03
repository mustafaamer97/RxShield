from database.loader import load_food_interactions


class DFIEngine:
    """
    Drug–Food Interaction Engine
    """

    def __init__(self):
        self.food_db = load_food_interactions()

    def find_interactions(self, drug_name: str):
        """
        Returns the food interaction record for a drug.

        Parameters
        ----------
        drug_name : str

        Returns
        -------
        dict | None
        """

        if not drug_name:
            return None

        drug = drug_name.strip().casefold()

        for item in self.food_db:

            name = item.get("name", "").strip().casefold()

            if name == drug:
                return {
                    "drug": item.get("name"),
                    "food_interactions": item.get("food_interactions", []),
                    "reference": item.get("reference", "")
                }

        return None

    def has_interaction(self, drug_name: str) -> bool:
        """
        Returns True if food interactions exist.
        """

        return self.find_interactions(drug_name) is not None
