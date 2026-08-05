from database.loader import DRUGS, NAME_TO_ID


class DrugInfoEngine:

    def __init__(self):
        self.drugs = DRUGS

    def get_info(self, drug_name):

        if not drug_name:
            return None

        query = drug_name.strip().lower()

        drug_id = NAME_TO_ID.get(query)

        if drug_id:
            return self.drugs.get(drug_id)

        return None
