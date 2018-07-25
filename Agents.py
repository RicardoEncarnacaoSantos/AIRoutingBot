# -----------------------------------------------------
# Agents module by Ricardo Santos.
# Defines some fictional agent profiles.
# -----------------------------------------------------

class Agents(object):
    """ Some hardcoded agent info to be used by the routing algorithm.
        Corresponds to all the agents in the contact center.
    """

    def __init__(self):
        self.agents = [
            {"agent id": 0, "name": "Mike",   "en": 0.75, "es": 0.75, "support": 1.00, "sales": 0.00},
            {"agent id": 1, "name": "Sandra", "en": 0.50, "es": 1.00, "support": 1.00, "sales": 0.00},
            {"agent id": 2, "name": "John",   "en": 1.00, "es": 0.00, "support": 0.00, "sales": 1.00},
            {"agent id": 3, "name": "Betty",  "en": 0.50, "es": 0.50, "support": 0.00, "sales": 1.00},
            {"agent id": 4, "name": "Harry",  "en": 0.75, "es": 0.00, "support": 1.00, "sales": 1.00},
            {"agent id": 5, "name": "Chris",  "en": 0.20, "es": 0.75, "support": 1.00, "sales": 1.00}]


    def get_agent_by_id(self, agent_id):
        for agent in self.agents:
            if agent["agent id"]==agent_id:
                return agent
        return None

    def get_agent_name(self, agent_id):
        agent = self.get_agent_by_id(agent_id)
        if not agent is None:
            return agent["name"]
        else:
            return "Unknown"

