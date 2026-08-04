from database.loader import load_drug_info


class DrugInfoEngine:
    def __init__(self):
        self.drugs = load_drug_info()

    def get_info(self, drug_name: str):
        """
        Returns full drug information from drug_info.json
        """

        if not drug_name:
            return None

        query = drug_name.strip().casefold()

        for drug in self.drugs:

            name = drug.get("name", "").strip().casefold()

            if name == query:
                return drug

            # Flexible matching
            if query in name or name in query:
                return drug

        return None
