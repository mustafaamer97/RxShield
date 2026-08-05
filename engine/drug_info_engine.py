from database.loader import load_drug_info


class DrugInfoEngine:

    def __init__(self):
        self.drugs = load_drug_info()

    def get_info_by_id(self, drug_id: str):
        """
        Returns drug information using DrugBank ID.
        """

        if not drug_id:
            return None

        return self.drugs.get(drug_id)

    def get_info(self, drug_name: str):
        """
        Optional fallback search by name.
        """

        if not drug_name:
            return None

        query = drug_name.strip().casefold()

        for drug in self.drugs.values():

            name = drug.get("name", "").strip().casefold()

            if name == query:
                return drug

            if query in name or name in query:
                return drug

        return None
