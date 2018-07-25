# -----------------------------------------------------
# CRM module by Ricardo Santos.
# Defines some fictional customer profiles and
# interactions between those customers and the 
# contact center.
# -----------------------------------------------------

class CRM(object):
    """ Some hardcoded customer info to be used by the routing algorithm.
    """

    def __init__(self):
        self.contacts = [
            {"contact id": 0, "name": "Mary", "age": 26, "postal code": "WC2N-5DU"},
            {"contact id": 1, "name": "Arnold", "age": 41, "postal code": "10005"},
            {"contact id": 2, "name": "Ferdinand", "age": 35, "postal code": "28000-070"}]

        self.history = [
            {"contact id": 0, "handled by": 0, "language": "en", "sentiment": 0.50, "category": "support", "score": 0.70 },
            {"contact id": 0, "handled by": 1, "language": "en", "sentiment": 0.20, "category": "support", "score": 0.90 },
            {"contact id": 1, "handled by": 5, "language": "en", "sentiment": 0.10, "category": "support", "score": 0.30 },
            {"contact id": 2, "handled by": 3, "language": "es", "sentiment": 0.50, "category": "sales",   "score": 0.85 },
            {"contact id": 2, "handled by": 5, "language": "es", "sentiment": 0.30, "category": "support", "score": 0.70 },
            {"contact id": 2, "handled by": 1, "language": "es", "sentiment": 0.90, "category": "sales",   "score": 0.00 },
            {"contact id": 1, "handled by": 4, "language": "en", "sentiment": 0.20, "category": "support", "score": 0.00 },
            {"contact id": 1, "handled by": 5, "language": "en", "sentiment": 0.00, "category": "support", "score": 0.85 },
            {"contact id": 0, "handled by": 1, "language": "en", "sentiment": 0.50, "category": "support", "score": 0.75 },
            {"contact id": 0, "handled by": 2, "language": "en", "sentiment": 1.00, "category": "sales",   "score": 0.20 },
            {"contact id": 0, "handled by": 3, "language": "en", "sentiment": 0.80, "category": "sales",   "score": 0.00 },
            {"contact id": 1, "handled by": 2, "language": "en", "sentiment": 0.50, "category": "sales",   "score": 0.80 },
            {"contact id": 1, "handled by": 3, "language": "en", "sentiment": 0.60, "category": "sales",   "score": 0.00 },
            {"contact id": 2, "handled by": 5, "language": "es", "sentiment": 0.90, "category": "sales",   "score": 1.00 },
            {"contact id": 1, "handled by": 4, "language": "en", "sentiment": 0.10, "category": "support", "score": 0.90 },
            {"contact id": 2, "handled by": 5, "language": "es", "sentiment": 1.00, "category": "sales",   "score": 1.00 },
            {"contact id": 0, "handled by": 0, "language": "en", "sentiment": 0.40, "category": "support", "score": 0.60 },
            {"contact id": 1, "handled by": 4, "language": "en", "sentiment": 0.20, "category": "support", "score": 1.00 },
            {"contact id": 2, "handled by": 3, "language": "es", "sentiment": 0.90, "category": "sales",   "score": 1.00 }]


    def get_contact_by_id(self, contact_id):
        for contact in self.contacts:
            if contact["contact id"]==contact_id:
                return contact
        return None

    def get_contact_name(self, contact_id):
        contact = self.get_contact_by_id(contact_id)
        if not contact is None:
            return contact["name"]
        else:
            return "Unknown"


